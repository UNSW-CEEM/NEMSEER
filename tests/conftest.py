import random
from datetime import datetime, timedelta

import grequests  # type: ignore
import pytest

from nemseer.downloader import get_sqlloader_years_and_months
from nemseer.nemseer import download_raw_data
from nemseer.query import Query

assert grequests


@pytest.fixture(scope="module")
def get_test_year_and_month():
    years_months = get_sqlloader_years_and_months()
    test_index = int(len(years_months) / 2)
    test_year = list(years_months.keys())[test_index]
    test_month = years_months[test_year][5]
    return (test_year, test_month)


@pytest.fixture(scope="module")
def valid_download_datetimes():
    run_start = "2021/02/01 00:00"
    run_end = "2021/02/05 00:00"
    forecasted_start = "2021/02/08 00:00"
    forecasted_end = "2021/02/08 23:55"
    return run_start, run_end, forecasted_start, forecasted_end


@pytest.fixture(scope="module")
def download_file_to_cache(tmp_path_factory, valid_download_datetimes):
    (
        run_start,
        run_end,
        forecasted_start,
        forecasted_end,
    ) = valid_download_datetimes
    tmp_dir = tmp_path_factory.mktemp("raw_cache")
    download_raw_data(
        run_start,
        run_end,
        forecasted_start,
        forecasted_end,
        "MTPASA",
        "REGIONRESULT",
        tmp_dir,
    )
    return Query.initialise(
        run_start,
        run_end,
        forecasted_start,
        forecasted_end,
        "MTPASA",
        "REGIONRESULT",
        tmp_dir,
    )


@pytest.fixture(scope="module")
def gen_datetime(n: int = 1):
    """Generate a datetime in format yyyy-mm-dd hh:mm:ss.000000

    From this gist: https://gist.github.com/rg3915/db907d7455a4949dbe69
    """
    dts = []
    for _ in range(0, n):
        min_year = 2012
        max_year = datetime.now().year
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        dts.append(start + (end - start) * random.random())
    if n == 1:
        return dts.pop()
    else:
        return dts
