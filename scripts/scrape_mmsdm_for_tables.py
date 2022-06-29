import os
import requests
import re

from bs4 import BeautifulSoup
from nemseer.downloader import USR_AGENT_HEADER, MMSDM_ARCHIVE_URL
from typing import List


def request_content(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=USR_AGENT_HEADER)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def get_months(url: str) -> List[int]:
    """
    """
    soup = request_content(url)
    months = []
    for link in soup.find_all('a'):
        url = link.get('href')
        findmonth = re.match(r".*[0-9]{4}_([0-9]{2})", url)
        if not findmonth:
            continue
        else:
            month = findmonth.group(1)
            months.append(int(month))
    unique = list(set(months))
    return unique


def get_years_and_months() -> List[int]:
    """
    """
    soup = request_content(MMSDM_ARCHIVE_URL)
    yearmonths = {}
    for link in soup.find_all('a'):
        url = link.get('href')
        findyear = re.match(r".*([0-9]{4}).*", url)
        if not findyear:
            continue
        else:
            year = int(findyear.group(1))
            months = get_months(MMSDM_ARCHIVE_URL + f'/{year}/')
            yearmonths[year] = months
    return yearmonths


def construct_mmsdm_yearmonth_url(year: int, month: int) -> str:
    url = (
        MMSDM_ARCHIVE_URL + f'/{year}/MMSDM_{year}_'
        + f'{str(month).rjust(2, "0")}/'
           )
    return url


def get_tables(url) -> List[str]:
    """
    """
    soup = request_content


        

