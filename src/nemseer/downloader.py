import logging
import shutil
from datetime import datetime
from itertools import cycle
from pathlib import Path
from re import match
from typing import Dict, Generator, List
from zipfile import BadZipFile, ZipFile

import psutil
import requests
from attrs import define, field
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from .data import (
    DEPRECATED_TABLES,
    ENUMERATED_TABLES,
    FORECAST_TYPES,
    INVALID_STUBS_FILE,
    MMSDM_ARCHIVE_URL,
    PREDISP_ALL_DATA,
    USER_AGENTS,
)
from .data_handlers import clean_forecast_csv
from .query import (
    Query,
    _construct_sqlloader_filename,
    _enumerate_tables,
    generate_sqlloader_filenames,
)

logger = logging.getLogger(__name__)


def _validate_forecast_type(forecast_type: str):
    """Check user-supplied forecast type is valid"""
    if forecast_type not in FORECAST_TYPES:
        raise ValueError(f"Forecast type should be one of {FORECAST_TYPES}")


def _build_useragent_generator(n: int) -> Generator[str, None, None]:
    """Generator function that cycles through user agents for GET requests.

    Generator function that cycles through user agents to yield n user agents
    in total. Doing so minimises 403 Forbidden errors when scraping.

    Args:
        n: Number of user agents, i.e. number of GET requests.
    Yields:
        useragent: A user agent.
    """
    inf_agents = cycle(USER_AGENTS)
    n_iterator = range(n)
    for _, useragent in zip(n_iterator, inf_agents):
        yield useragent


def _build_nemweb_get_header(useragent: str) -> Dict[str, str]:
    """Builds request header for GET requests from NEMWeb

    Args:
        useragent: User-Agent string to use
    Returns:
        Dict that can be used as a request header
    """
    header = {
        "Host": "www.nemweb.com.au",
        "User-Agent": useragent,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            + "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    return header


def _request_content(
    url: str, useragent: str, additional_header: Dict = {}
) -> requests.Response:
    """Initiates a GET request with header information.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
            additional header information to GET request.
    Returns:
        requests Response object.
    """
    header = _build_nemweb_get_header(useragent)
    if additional_header:
        header.update(additional_header)
    r = requests.get(url, headers=header)
    return r


def _rerequest_to_obtain_soup(
    url: str, useragent: str, additional_header: Dict = {}
) -> BeautifulSoup:
    """Continually launches requests until a 200 (OK) code is returned.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
            additional header information to GET request.

    Returns:
        BeautifulSoup object with parsed HTML.

    """
    r = _request_content(url, useragent, additional_header=additional_header)
    while (ok := r.status_code == requests.status_codes.codes["OK"]) < 1:
        r = _request_content(url, useragent, additional_header=additional_header)
        if r.status_code == requests.status_codes.codes["OK"]:
            ok += 1
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def _construct_yearmonth_url(
    year: int, month: int, forecast_type: str, all_data: bool = False
) -> str:
    """Constructs MMSDM Historical Data SQLLoader Base URL for a given year and month.

    Handles exceptions to naming rules and complete tables (`PREDISP_ALL_DATA`)
    for `PREDISPATCH` when `forecast_type` = "PREDISPATCH" and `all_data` = True.

    N.B. Can be extended to handle `P5MIN_ALL_DATA`, but this appears to be similar to
    `P5MIN` data in `DATA` directory. Files in this directory have `ALL` in the name.

    Args:
        year: Year
        month: Month
        forecast_type: One of :data:`nemseer.forecast_types`
        all_data (optional): Default False. Points to `ALL_DATA` folder for PD
    Returns:
        Constructed URL as a string.
    """
    base_url = (
        MMSDM_ARCHIVE_URL
        + f"{year}/MMSDM_{year}_"
        + f'{str(month).rjust(2, "0")}/MMSDM_Historical_Data_SQLLoader/'
    )
    if forecast_type == "PREDISPATCH" and all_data:
        data_url = base_url + "PREDISP_ALL_DATA/"
    else:
        data_url = base_url + "DATA/"
    return data_url


def _construct_sqlloader_forecastdata_url(
    year: int, month: int, forecast_type: str, table: str
) -> str:
    """Constructs URL that points to a MMSDM Historical Data SQLLoader zip file

    Handles exceptions to naming rules and complete tables (`PREDISP_ALL_DATA`)
    for `PREDISPATCH`.

    Args:
        year: Year
        month: Month
        forecast_type: One of :data:`nemseer.forecast_types`
    Returns:
        URL to zip file
    """
    if (
        forecast_type == "PREDISPATCH"
        and (table_basename := match(r"([A-Z_]*)[0-9]?", table))
        and table_basename.group(1) in PREDISP_ALL_DATA
    ):
        data_url = _construct_yearmonth_url(year, month, forecast_type, all_data=True)
    else:
        data_url = _construct_yearmonth_url(year, month, forecast_type)
    fn = _construct_sqlloader_filename(year, month, forecast_type, table)
    url = data_url + fn + ".zip"
    return url


def _get_captured_group_from_links(url: str, regex: str) -> List[str]:
    """Returns list of unique captured groups from MMSDM Historical Data SQLLoader page

    For a year and month in the MMSDM Historical Data SQLLoader, returns captured groups
    associated with a particular `forecast_type`. Primarily used to obtain table names.

    Args:
        year: Year
        month: Month
        forecast_type: One of :data:`nemseer.forecast_types`
        regex: Regular expression pattern, with one group capture
    Returns:
        A list of unique captured groups (one for each link on the page of tables)
    """
    soup = _rerequest_to_obtain_soup(url, next(_build_useragent_generator(1)))
    links = [link.get("href") for link in soup.find_all("a")]
    tables = []
    for link in links:
        if mo := match(regex, link):
            tables.append(mo.group(1).lstrip("_"))
    return list(set(tables))


def get_sqlloader_forecast_tables(
    year: int, month: int, forecast_type: str, actual: bool = False
) -> List[str]:
    """Requestable tables of particular forecast type on MMSDM Historical Data SQLLoader

    If :attr:`actual` = False, provides a list of tables that can be requested via
    `nemseer`.

    If :attr:`actual` = True, returns actual tables available via NEMWeb, including all
    tables that are enumerated.

    N.B.:
      - Removes numbering from enumerated tables for `P5MIN`
        - e.g. `CONSTRAINTSOLUTION(x)` are all reduced to `CONSTRAINTSOLUTION`

    Examples:
        See :ref:`querying table availability <quick_start:table availability>`
    Args:
        year: Year
        month: Month
        forecast_type: One of :data:`nemseer.forecast_types`

    Returns:
        List of tables associated with that forecast type for that period
    """
    _validate_forecast_type(forecast_type)
    if actual:
        table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_0-9]*)_[0-9]*.zip"
    else:
        table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_]*)[0-9]?_[0-9]*.zip"
    data_url = _construct_yearmonth_url(year, month, forecast_type)
    tables = _get_captured_group_from_links(data_url, table_capture)
    if forecast_type == "PREDISPATCH":
        predisp_all_url = _construct_yearmonth_url(
            year, month, forecast_type, all_data=True
        )
        predisp_all_tables = _get_captured_group_from_links(
            predisp_all_url, table_capture
        )
        tables.extend(predisp_all_tables)
    return sorted(tables)


def get_sqlloader_years_and_months() -> Dict[int, List[int]]:
    """Years and months with data on NEMWeb MMSDM Historical Data SQLLoader
    Examples:
        See :ref:`querying date ranges \
        <quick_start:date range of available data>`
    Returns:
        Months mapped to each year. Data is available for each of these months.
    """

    def _get_months(url: str, useragent: str) -> List[int]:
        """Pull months from scraped links with YYYY-MM date format

        Args:
            url: url for GET request.
            header: useragent to pass to GET request.
        Returns:
            List of unique months (as integers).
        """
        referer_header = {"Referer": MMSDM_ARCHIVE_URL}
        soup = _rerequest_to_obtain_soup(
            url, useragent, additional_header=referer_header
        )
        months = []
        for link in soup.find_all("a"):
            url = link.get("href")
            findmonth = match(r".*[0-9]{4}_([0-9]{2})", url)
            if not findmonth:
                continue
            else:
                month = findmonth.group(1)
                months.append(int(month))
        unique = list(set(months))
        return unique

    useragent = next(_build_useragent_generator(1))
    soup = _rerequest_to_obtain_soup(MMSDM_ARCHIVE_URL, useragent)
    links = soup.find_all("a")
    nlinks = len(links)
    yearmonths = {}
    for useragent, link in zip(_build_useragent_generator(nlinks), links):
        url = link.get("href")
        findyear = match(r".*([0-9]{4}).*", url)
        if not findyear:
            continue
        else:
            year = int(findyear.group(1))
            months = _get_months(MMSDM_ARCHIVE_URL + f"{year}/", useragent)
            yearmonths[year] = months
    return yearmonths


def get_unzipped_csv(url: str, raw_cache: Path) -> None:
    """Unzipped (single) csv file downloaded from `url` to :term:`raw_cache`

    This function:

    1. Downloads zip file in chunks to limit memory use and enable progress bar
    2. Validates that the zip contains a single file that has the same name as the zip
    3. If the zip file is invalid, writes the file stub to `.invalid_aemo_files.txt`

    Args:
        url: URL of zip
        raw_cache: Path to save zip. See :term:`raw_cache`.
    Returns:
        None. Extracts csvs to :attr:`raw_cache`.
    """

    def _invalid_zip_to_file(invalid_files: Path, filename: str) -> None:
        """Ensure that any invalid file is noted in the `invalid_files` text file"""
        with open(invalid_files, "a+") as f:
            f.seek(0)
            existing = [line.strip() for line in f.readlines()]
            if filename in existing:
                pass
            else:
                f.write(f"{filename}\n")
        return None

    file_name = Path(url).name
    header = _build_nemweb_get_header(next(_build_useragent_generator(1)))
    file_path = raw_cache / Path(file_name)
    with requests.get(url, headers=header, stream=True) as resp:
        total_length = int(resp.headers.get("Content-Length", 0))
        resp.raise_for_status()
        with tqdm.wrapattr(resp.raw, "read", desc=file_name, total=total_length) as raw:
            with open(file_path, "wb") as fout:
                shutil.copyfileobj(raw, fout)
    z = ZipFile(file_path)
    if (
        len(csvfn := z.namelist()) == 1
        and (zfn := match(".*DATA/(.*).zip", url))
        and (fn := match("(.*).[cC][sS][vV]", csvfn.pop()))
        and (fn.group(1) == zfn.group(1))
    ):
        try:
            z.extractall(raw_cache)
            z.close()
        except BadZipFile:
            logging.error(f"{z.testzip()} invalid or corrupted")
            invalid_files = raw_cache / Path(INVALID_STUBS_FILE)
            _invalid_zip_to_file(invalid_files, fn.group(1))
        Path(file_path).unlink()
    else:
        raise ValueError(f"Unexpected contents in zipfile from {url}")


def _validate_tables_on_run_start(instance, attribute, value) -> None:
    """Validates tables for the provided forecast type.

    Checks user-supplied tables against tables available in MMS Historical
    Data SQLLoader for the month and year of run_start.
    """
    start_dt = instance.run_start
    actual_tables = get_sqlloader_forecast_tables(
        start_dt.year, start_dt.month, instance.forecast_type, actual=True
    )
    requestable_tables = get_sqlloader_forecast_tables(
        start_dt.year, start_dt.month, instance.forecast_type, actual=False
    )
    if instance.forecast_type in DEPRECATED_TABLES.keys() and any(
        dep_tabs := [
            table
            for table in value
            if table in DEPRECATED_TABLES[instance.forecast_type]
        ]
    ):
        logging.warning(f"{instance.forecast_type} {dep_tabs} deprecated.")
    if not set(value).issubset(set(actual_tables)):
        raise ValueError(
            "Table(s) not available from MMS Historical Data SQL Loader"
            + f" (for {start_dt.month}/{start_dt.year}).\n"
            + f"Tables include: {requestable_tables}"
        )


@define(kw_only=True)
class ForecastTypeDownloader:
    """:class:`ForecastTypeDownloader` can initiate csv downloads and convert
    :term:`raw_cache` csvs to the parquet format.

    Attributes:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecast_type: One of :data:`nemseer.forecast_types`
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        raw_cache: Path to download raw data to. Can reuse or build a
            new :term:`raw_cache`.
    """

    run_start: datetime
    run_end: datetime
    forecast_type: str
    tables: List[str] = field(validator=_validate_tables_on_run_start)
    raw_cache: Path

    @classmethod
    def from_Query(cls, query: Query) -> "ForecastTypeDownloader":
        """Constructor method for :class:`ForecastTypeDownloader` from
        :class:`Query <nemseer.query.Query>`"""
        tables = query.tables
        for ftype in ENUMERATED_TABLES:
            if query.forecast_type == ftype:
                for table, enumerate_to in ENUMERATED_TABLES[ftype]:
                    if table in tables:
                        tables = _enumerate_tables(tables, table, enumerate_to)

        return cls(
            run_start=query.run_start,
            run_end=query.run_end,
            forecast_type=query.forecast_type,
            tables=tables,
            raw_cache=query.raw_cache,
        )

    def download_csv(self) -> None:
        """Downloads and unzips zip files given query loaded into
        :class:`ForecastTypeDownloader`

        This method will only download and unzip the relevant zip/csv if the
        corresponding `.parquet` file is not located in the specified :attr:`raw_cache`.
        """
        filename_data = generate_sqlloader_filenames(
            self.run_start, self.run_end, self.forecast_type, self.tables
        )
        invalid_or_corrupted_stubfile = self.raw_cache / Path(INVALID_STUBS_FILE)
        for metadata in filename_data.keys():
            fname = filename_data[metadata]
            (year, month, table) = metadata
            if (self.raw_cache / Path(fname + ".parquet")).exists():
                logging.info(f"{table} for {month}/{year} in raw_cache")
                continue
            else:
                if invalid_or_corrupted_stubfile.exists():
                    with open(invalid_or_corrupted_stubfile, "r") as f:
                        invalid_or_corrupted = f.readlines()
                    check_files = [f.strip() for f in invalid_or_corrupted]
                    if fname in check_files:
                        logging.warning(
                            f"{fname} previously found to be invalid/corrupted. "
                            + "Skipping download for this file. "
                            + "If downloading manually works, remove from "
                            + ".invalid_aemo_files.txt in raw_cache. "
                            + "Otherwise, contact AEMO."
                        )
                        continue
                url = _construct_sqlloader_forecastdata_url(
                    year, month, self.forecast_type, table
                )
                logger.info(f"Downloading and unzipping {table} for {month}/{year}")
                get_unzipped_csv(url, self.raw_cache)

    def convert_to_parquet(self, keep_csv=False) -> None:
        """Converts all CSVs in the :attr:`raw_cache` to parquet

        Warning:
            A warning is printed if the filesize is greater than half of available
            memory as :class:`pandas.DataFrame` consumes more than the file size in
            memory.
        """
        csvs: List[Path] = []
        for forecast_type in FORECAST_TYPES:
            csvs.extend(Path(self.raw_cache).glob(f"*{forecast_type}*.[Cc][Ss][Vv]"))
        for csv in csvs:
            if csv.stat().st_size * 2 >= psutil.virtual_memory().available:
                logging.warning(
                    f"Attempting to convert {csv} to parquet,"
                    + " but your available system memory may be too low for this."
                )
            df = clean_forecast_csv(csv)
            parquet_name = csv.name[0:-3] + "parquet"
            if not csv.with_name(parquet_name).exists():
                logging.info(f"Converting {csv.name} to parquet")
                df.to_parquet(csv.with_name(parquet_name))
            else:
                logging.info(f"{parquet_name} already exists")
            if not keep_csv:
                csv.unlink()
