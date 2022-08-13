import io
import logging
from itertools import cycle
from pathlib import Path
from re import match, search
from typing import Dict, Generator, List
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup

from .data import MMSDM_ARCHIVE_URL, USER_AGENTS

logger = logging.getLogger(__name__)


def _build_useragent_generator(n: int) -> Generator:
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
        year: Year
        month: Month
        forecast_type: `P5MIN`, `PREDISPATCH`, `PDPASA`, `STPASA` or `MTPASA`
        table: The name of the table required
    Returns:
        URL pointing to forecast data zipfile on NEMWeb
    """
    base_url = _construct_sqlloader_yearmonth_url(year, month)
    (stryear, strmonth) = (str(year), str(month).rjust(2, "0"))
    if forecast_type == "PREDISPATCH" and forecast_type != "MNSPBIDTRK":
        prefix = f"PUBLIC_DVD_{forecast_type}{table}"
    else:
        prefix = f"PUBLIC_DVD_{forecast_type}_{table}"
    url = base_url + prefix + f"_{stryear}{strmonth}010000.zip"
    return url


def _get_captured_group_from_links(
    year: int, month: int, forecast_type: str, regex: str
) -> List[str]:
    """Returns a list of unique captured groups from a MMSDM Historical Data SQLLOader page

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
    """Available tables for a particular forecast type on MMSDM Historical Data SQLLoader

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
    tables = _get_captured_group_from_links(year, month, forecast_type, table_capture)
    return tables


def get_sqlloader_forecast_tables(
    year: int, month: int, forecast_type: str
) -> List[str]:
    """Requestable tables for a particular forecast type on MMSDM Historical Data SQLLoader

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
    valid_types = ("P5MIN", "PREDISPATCH", "STPASA", "MTPASA")
    if forecast_type not in valid_types:
        raise ValueError(f"Forecast type should be one of {valid_types}")
    table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_]*)[0-9]?_[0-9]*.zip"
    tables = _get_captured_group_from_links(year, month, forecast_type, table_capture)
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


def get_sqlloader_filesize(
    year: int, month: int, forecast_type: str, table: str
) -> float:
    """File size in MB for MMSDM Historical Data SQLLoader file

    NEMWeb has file size in a column preceding the link to the file. This function
    scrapes and returns a megabyte filesize (NEMWeb file size is in bytes).

    Args:
        year: Year
        month: Month
        forecast_type: `P5MIN`, `PREDISPATCH`, `PDPASA`, `STPASA` or `MTPASA`
        table: The name of the table required
    Returns:
        File size in megabytes, rounded to nearest MB
    """
    valid_types = ("P5MIN", "PREDISPATCH", "STPASA", "MTPASA")
    if forecast_type not in valid_types:
        raise ValueError(f"Forecast type should be one of {valid_types}")
    parent_url = _construct_sqlloader_yearmonth_url(year, month)
    data_url = _construct_sqlloader_forecastdata_url(year, month, forecast_type, table)
    data_table = data_url.lstrip(parent_url)
    useragent = next(_build_useragent_generator(1))
    soup = _rerequest_to_obtain_soup(parent_url, useragent)
    if not (size_and_file := search(f"([0-9]*) {data_table}", soup.get_text())):
        raise ValueError(f" Cannot find file size for {data_table}")
    else:
        size = size_and_file.group(1)
        size = round(float(size) / (1024**2), 2)
    return size


def get_unzipped_csv(url: str, raw_cache: Path) -> None:
    """Downloads unzipped (single) csv file from `url` to `raw_cache`

    Validates that the zip contains a single file that has the same name as the zip

    Args:
        url: URL of zip
        raw_cache: Path to save zip
    Returns:
        None. Extracts csvs to `raw_cache`.
    """
    r = _request_content(url, next(_build_useragent_generator(1)))
    z = ZipFile(io.BytesIO(r.content))
    if (
        len(csvfn := z.namelist()) == 1
        and (zfn := match(".*/DATA/(.*).zip", url))
        and (fn := match("(.*).[cC][sS][vV]", csvfn.pop()))
        and (fn.group(1) == zfn.group(1))
    ):
        z.extractall(raw_cache)
    else:
        raise ValueError(f"Unexpected contents in zipfile from {url}")
