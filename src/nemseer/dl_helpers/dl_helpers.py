import requests

from bs4 import BeautifulSoup
from itertools import cycle
from re import match
from typing import Dict, List, Generator

from .urls import MMSDM_ARCHIVE_URL
from .user_agents import USER_AGENTS


def _build_useragent_generator(n: int) -> Generator:
    """Generator function that cycles through user agents for GET requests.

    Generator function that cycles through user agents to yield n user agents
    in total. Doing so avoids 403 Forbidden errors when scraping.

    Args:
        n: Number of user agents, i.e. number of GET requests.
    Yields:
        useragent: A user agent.
    """
    inf_agents = cycle(USER_AGENTS)
    n_iterator = range(n)
    for _, useragent in zip(n_iterator, inf_agents):
        yield useragent


def _request_content(url: str, useragent: str,
                     additional_header: Dict = {}) -> requests.Response:
    """Initiates a GET request with header information.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
            additional header information to GET request.
    Returns:
        requests Response object.
    """
    header = {
        "Host": "www.nemweb.com.au",
        "User-Agent": useragent,
        "Accept": ("text/html,application/xhtml+xml,application/xml;"
                   + "q=0.9,image/avif,image/webp,*/*;q=0.8"),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate", "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    if additional_header:
        header.update(additional_header)
    r = requests.get(url, headers=header)
    return r


def _rerequest_to_obtain_soup(url: str, useragent: str,
                              additional_header: Dict = {}) -> BeautifulSoup:
    """Continually launches requests until a 200 (OK) code is returned.

    Args:
        url: URL for GET request.
        useragent: User-Agent to use in header.
        additional_header: Empty dictionary as default. Can be used to add
            additional header information to GET request.

    Returns:
        BeautifulSoup object with parsed HTML.

    """
    r = _request_content(url, useragent,
                         additional_header=additional_header)
    ok = (r.status_code == requests.status_codes.codes['OK'])
    while ok < 1:
        r = _request_content(url, useragent,
                             additional_header=additional_header)
        if r.status_code == requests.status_codes.codes['OK']:
            ok += 1
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def _get_months(url: str, useragent: str) -> List[int]:
    """Pull months from scraped links with YYYY-MM date format

    Args:
        url: url for GET request.
        header: useragent to pass to GET request.
    Returns:
        List of unique months (as integers).
    """
    referer_header = {"Referer": MMSDM_ARCHIVE_URL}
    soup = _rerequest_to_obtain_soup(url, useragent,
                                     additional_header=referer_header)
    months = []
    for link in soup.find_all("a"):
        url = link.get('href')
        findmonth = match(r".*[0-9]{4}_([0-9]{2})", url)
        if not findmonth:
            continue
        else:
            month = findmonth.group(1)
            months.append(int(month))
    unique = list(set(months))
    return unique


def _get_years_and_months() -> Dict[int, List[int]]:
    """Checks months with data available, for each year from scraped link.

    Returns:
        Months mapped to each year. Data is available for each of these months.
    """
    useragent = next(_build_useragent_generator(1))
    soup = _rerequest_to_obtain_soup(MMSDM_ARCHIVE_URL, useragent)
    links = soup.find_all("a")
    nlinks = len(links)
    yearmonths = {}
    for useragent, link in zip(_build_useragent_generator(nlinks), links):
        url = link.get('href')
        findyear = match(r".*([0-9]{4}).*", url)
        if not findyear:
            continue
        else:
            year = int(findyear.group(1))
            months = _get_months(MMSDM_ARCHIVE_URL + f'{year}/',
                                 useragent)
            yearmonths[year] = months
    return yearmonths


def _construct_mmsdm_yearmonth_url(year: int, month: int) -> str:
    """Constructs MMSDM Historical Data SQLLoader URL for a given year and month

    Args:
        year: Year
        month: Month
    Returns:
        Constructed URL as a string.
    """
    url = (
        MMSDM_ARCHIVE_URL + f'{year}/MMSDM_{year}_'
        + f'{str(month).rjust(2, "0")}/MMSDM_Historical_Data_SQLLoader/'
        + 'DATA/'
           )
    return url


def _get_mmsdm_tables_for_yearmonths(year: int, month: int,
                                     forecast_type: str) -> List[str]:
    """For a month & year, get available tables for a particular forecast type.

    `table_capture` handles P5MIN tables that are spread across multiple files
      - e.g. CONSTRAINTSOLUTION1, CONSTRAINTSOLUTION2, etc.

    Args:
        year: Year
        month: Month
        forecast_type: AEMO forecast types (P5MIN, PREDISPATCH, STPASA, MTPASA)
    Returns:
        List of tables associated with that forecast type for that period
    """
    url = _construct_mmsdm_yearmonth_url(year, month)
    soup = _rerequest_to_obtain_soup(url, next(_build_useragent_generator(1)))
    links = [link.get('href') for link in soup.find_all("a")]
    table_capture = f".*/PUBLIC_DVD_{forecast_type}([A-Z_]*)[0-9]?_[0-9]*.zip"
    tables = set([
        match(table_capture, link).group(1).lstrip("_")
        for link in links if match(table_capture, link)
        ])
    return list(tables)
