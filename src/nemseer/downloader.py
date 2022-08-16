import logging
import shutil
from datetime import datetime
from itertools import cycle
from pathlib import Path
from re import match
from typing import Dict, Generator, List, Optional
from zipfile import ZipFile

import psutil
import requests
from attrs import define, field
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from .data_handlers import clean_forecast_csv
from .downloader_helpers.data import MMSDM_ARCHIVE_URL, USER_AGENTS
from .loader import Loader, _construct_sqlloader_filename, generate_sqlloader_filenames

logger = logging.getLogger(__name__)


def _validate_forecast_type(forecast_type: str):
    valid_types = ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA")
    if forecast_type not in valid_types:
        raise ValueError(f"Forecast type should be one of {valid_types}")


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


def _construct_sqlloader_yearmonth_url(year: int, month: int) -> str:
    """Constructs MMSDM Historical Data SQLLoader URL for a given year and month

    Args:
        year: Year
        month: Month
    Returns:
        Constructed URL as a string.
    """
    url = (
        MMSDM_ARCHIVE_URL
        + f"{year}/MMSDM_{year}_"
        + f'{str(month).rjust(2, "0")}/MMSDM_Historical_Data_SQLLoader/'
        + "DATA/"
    )
    return url


def _construct_sqlloader_forecastdata_url(
    year: int, month: int, forecast_type: str, table: str
) -> str:
    """Constructs URL that points to a MMSDM Historical Data SQLLoader zip file

    Handles exceptions to naming rules for `PREDISPATCH`

    Args:
    """
    base_url = _construct_sqlloader_yearmonth_url(year, month)
    fn = _construct_sqlloader_filename(year, month, forecast_type, table)
    url = base_url + fn + ".zip"
    return url


def _get_captured_group_from_links(year: int, month: int, regex: str) -> List[str]:
    """Returns list of unique captured groups from MMSDM Historical Data SQLLoader page

    For a year and month in the MMSDM Historical Data SQLLoader, returns captured groups
    associated with a particular `forecast_type`. Primarily used to obtain table names.

    Args:
        year: Year
        month: Month
        forecast_type: AEMO forecast types (`P5MIN`, `PREDISPATCH`, `STPASA`, `MTPASA`)
        regex: Regular expression pattern, with one group capture
    Returns:
        A list of unique captured groups (one for each link on the page of tables)
    """
    url = _construct_sqlloader_yearmonth_url(year, month)
    soup = _rerequest_to_obtain_soup(url, next(_build_useragent_generator(1)))
    links = [link.get("href") for link in soup.find_all("a")]
    tables = []
    for link in links:
        if mo := match(regex, link):
            tables.append(mo.group(1).lstrip("_"))
    return list(set(tables))


def _get_all_sqlloader_forecast_tables(
    year: int, month: int, forecast_type: str
) -> List[str]:
    """Available tables for particular forecast type on MMSDM Historical Data SQLLoader

    Private validator function that returns actual tables available via NEMWeb,
    including all tables that are enumerated.

    Args:
        year: Year
        month: Month
        forecast_type: AEMO forecast types (`P5MIN`, `PREDISPATCH`, `STPASA`, `MTPASA`)
    Returns:
        List of tables associated with that forecast type for that period
    """
    table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_0-9]*)_[0-9]*.zip"
    tables = _get_captured_group_from_links(year, month, table_capture)
    return tables


def get_sqlloader_forecast_tables(
    year: int, month: int, forecast_type: str
) -> List[str]:
    """Requestable tables of particular forecast type on MMSDM Historical Data SQLLoader

    Provides a list of tables that can be requested via `nemseer`.

    N.B.:
      - Removes numbering from enumerated tables for `P5MIN`
        - e.g. `CONSTRAINTSOLUTION(x)` are all reduced to `CONSTRAINTSOLUTION`

    Args:
        year: Year
        month: Month
        forecast_type: AEMO forecast types (`P5MIN`, `PREDISPATCH`, `STPASA`, `MTPASA`)
    Returns:
        List of tables associated with that forecast type for that period
    """
    _validate_forecast_type(forecast_type)
    table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_]*)[0-9]?_[0-9]*.zip"
    tables = _get_captured_group_from_links(year, month, table_capture)
    return tables


def get_sqlloader_years_and_months() -> Dict[int, List[int]]:
    """Years and months with data on NEMWeb MMSDM Historical Data SQLLoader

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
    """Unzipped (single) csv file downloaded from `url` to `raw_cache`

    1. Downloads zip file in chunks to limit memory use and enable progress bar
    2. Validates that the zip contains a single file that has the same name as the zip

    Args:
        url: URL of zip
        raw_cache: Path to save zip
    Returns:
        None. Extracts csvs to `raw_cache`.
    """
    file_name = Path(url).name
    header = _build_nemweb_get_header(next(_build_useragent_generator(1)))
    file_path = raw_cache / Path(file_name)
    with requests.get(url, headers=header, stream=True) as r:
        total_length = int(r.headers.get("Content-Length", 0))
        with tqdm.wrapattr(r.raw, "read", desc=file_name, total=total_length) as raw:
            with open(file_path, "wb") as fout:
                shutil.copyfileobj(raw, fout)
    z = ZipFile(file_path)
    if (
        len(csvfn := z.namelist()) == 1
        and (zfn := match(".*/DATA/(.*).zip", url))
        and (fn := match("(.*).[cC][sS][vV]", csvfn.pop()))
        and (fn.group(1) == zfn.group(1))
    ):
        z.extractall(raw_cache)
        Path(file_path).unlink()
    else:
        raise ValueError(f"Unexpected contents in zipfile from {url}")


def _enumerate_tables(tables: List[str], table_str: str, range_to: int):
    """Given a table name, populates a list with enumerated table names

    For example, given 'CONSTRAINTSOLUTION' and `range_to`=3, will populate
    `tables` with ['CONSTRAINTSOLUTION1',...,'CONSTRAINTSOLUTION3'].

    Args:
        tables: Table list
        table_str: Table string to enumerate
        range_to: Integer to enumerate to
    Returns:
        `tables` with enumerated `table_str`
    """
    tables.remove(table_str)
    for i in range(1, range_to + 1):
        tables.append(f"{table_str}{i}")
    return tables


def _validate_tables_on_forecast_start(instance, attribute, value):
    """Validates tables for the provided forecast type.

    Checks user-supplied tables against tables available in MMS Historical
    Data SQL Loader for the month and year of forecast_start.
    """
    start_dt = instance.forecast_start
    tables = _get_all_sqlloader_forecast_tables(
        start_dt.year, start_dt.month, instance.forecast_type
    )
    if not set(value).issubset(set(tables)):
        raise ValueError(
            "Table(s) not available from MMS Historical Data SQL Loader"
            + f" (for {start_dt.month}/{start_dt.year}).\n"
            + f"Tables include: {tables}"
        )


@define(kw_only=True)
class ForecastTypeDownloader:
    forecast_start: datetime
    forecast_end: datetime
    forecast_type: str
    tables: List[str] = field(validator=_validate_tables_on_forecast_start)
    raw_cache: Optional[str] = field(default=None)

    @classmethod
    def from_Loader(cls, loader: Loader):
        """Constructor method for ForecastTypeDownloader from Loader."""
        tables = loader.tables
        if "CONSTRAINTSOLUTION" in tables and loader.forecast_type == "P5MIN":
            tables = _enumerate_tables(tables, "CONSTRAINTSOLUTION", 4)

        return cls(
            forecast_start=loader.forecast_start,
            forecast_end=loader.forecast_end,
            forecast_type=loader.forecast_type,
            tables=tables,
            raw_cache=loader.raw_cache,
        )

    def download_csv(self):
        """Downloads and unzips zip files given query loaded into ForecastTypeDownloader

        This method will only download and unzip the relevant zip/csv if the
        corresponding `.parquet` file is not located in the specified `raw_cache`.
        """
        yearmonths, fnames = generate_sqlloader_filenames(
            self.forecast_start, self.forecast_end, self.forecast_type, self.tables
        )
        for ((year, month), fname) in zip(yearmonths, fnames):
            raw_table = match(f"^PUBLIC_DVD_{self.forecast_type}(.*)_[0-9]*$", fname)
            table = raw_table.group(1).lstrip("_")
            if (self.raw_cache / Path(fname + ".parquet")).exists():
                logging.info(f"{table} for {month}/{year} in raw_cache")
                continue
            else:
                url = _construct_sqlloader_forecastdata_url(
                    year, month, self.forecast_type, table
                )
                logger.info(f"Downloading and unzipping {table} for {month}/{year}")
                get_unzipped_csv(url, self.raw_cache)

    def convert_to_parquet(self, keep_csv=False):
        """Converts all CSVs in the `raw_cache` to parquet

        Logs a warning if the filesize is greater than half of available memory.
        pandas DataFrames consume more than the file size in memory.
        """
        csvs = list(Path(self.raw_cache).glob("*.[Cc][Ss][Vv]"))
        for csv in csvs:
            if csv.stat().st_size * 2 >= psutil.virtual_memory().available:
                logging.warning(
                    f"Attempting to convert {csv} to parquet,"
                    + " but your available system memory may be too low for this."
                )
            logging.info(f"Converting {csv.name} to parquet")
            df = clean_forecast_csv(csv)
            parquet_name = csv.name[0:-3] + "parquet"
            df.to_parquet(csv.with_name(parquet_name))
            if not keep_csv:
                csv.unlink()
