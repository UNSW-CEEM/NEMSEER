import random
from datetime import datetime, timedelta

import grequests  # type: ignore
import pytest

from nemseer.forecast_type.run_time_generators import generate_runtimes
from nemseer.nemseer import compile_data, download_raw_data
from nemseer.query import Query

assert grequests


@pytest.fixture(scope="module")
def get_test_year_and_month():
    return 2024, 8


@pytest.fixture(scope="session")
def valid_download_datetimes():
    run_start = "2025/02/01 00:00"
    run_end = "2025/02/05 00:00"
    forecasted_start = "2025/02/08 00:00"
    forecasted_end = "2025/02/08 23:55"
    return run_start, run_end, forecasted_start, forecasted_end


@pytest.fixture(scope="session")
def valid_download_datetimes_pre202408():
    # Some tests only make sense on data prior to Aug 2024
    run_start = "2020/02/01 00:00"
    run_end = "2020/02/05 00:00"
    forecasted_start = "2020/02/08 00:00"
    forecasted_end = "2020/02/08 23:55"
    return run_start, run_end, forecasted_start, forecasted_end


@pytest.fixture(scope="session")
def download_file_to_cache(tmp_path_factory, valid_download_datetimes):
    (
        run_start,
        run_end,
        forecasted_start,
        forecasted_end,
    ) = valid_download_datetimes
    tmp_dir = tmp_path_factory.mktemp("raw_cache")
    download_raw_data(
        "MTPASA",
        "REGIONRESULT",
        tmp_dir,
        run_start=run_start,
        run_end=run_end,
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


@pytest.fixture(scope="session")
def compile_data_to_processed_cache(tmp_path_factory):
    queries = {
        "STPASA": "INTERCONNECTORSOLN",
        "PREDISPATCH": "REGIONSUM",
        "P5MIN": "CASESOLUTION",
    }
    forecasted_start = "2022/03/15 00:00"
    forecasted_end = "2022/03/17 00:00"
    raw_cache = tmp_path_factory.mktemp("raw_cache")
    processed_cache = tmp_path_factory.mktemp("processed_cache")
    query_metadata = {}
    for forecast_type, table in queries.items():
        run_start, run_end = generate_runtimes(
            forecasted_start, forecasted_end, forecast_type
        )
        query_metadata[forecast_type] = {
            "run_start": run_start,
            "run_end": run_end,
            "forecasted_start": forecasted_start,
            "forecasted_end": forecasted_end,
            "forecast_type": forecast_type,
            "tables": table,
            "raw_cache": raw_cache,
            "processed_cache": processed_cache,
        }
        compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=raw_cache,
            processed_cache=processed_cache,
            data_format="xr",
        )
        compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=raw_cache,
            processed_cache=processed_cache,
            data_format="df",
        )
    return query_metadata


def _gen_datetime():
    """Generate a datetime in format yyyy-mm-dd hh:mm:ss.000000

    From this gist: https://gist.github.com/rg3915/db907d7455a4949dbe69
    """
    # Earliest runtime data on nemweb in correct format is 2015 (Jan)
    # MTPASA tests go back 2 years 15 days so make earliest start Feb 2017 for tests
    # This will give latest forecast time of Feb 2026 which works
    min_year = 2017
    max_year = 2025
    start = datetime(min_year, 2, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


@pytest.fixture
def gen_datetime():
    """Generate a datetime in format yyyy-mm-dd hh:mm:ss.000000

    From this gist: https://gist.github.com/rg3915/db907d7455a4949dbe69
    """
    return _gen_datetime()


@pytest.fixture
def gen_n_datetimes(request):
    dts = []
    for _ in range(0, request.param):
        dts.append(_gen_datetime())
    if request.param == 1:
        return dts.pop()
    else:
        return dts


@pytest.fixture
def fix_forecasted_dt():
    def _method(forecasted_dt: datetime, forecast_type: str):
        """Fixes output from _gen_datetime to create a valid `forecasted` time"""
        forecasted_dt = forecasted_dt.replace(second=0, microsecond=0)
        if forecast_type == "P5MIN":
            forecasted_dt = forecasted_dt.replace(minute=25)
        elif forecast_type in ["PDPASA", "PREDISPATCH"]:
            forecasted_dt = forecasted_dt.replace(minute=30)
        elif forecast_type == "MTPASA":
            forecasted_dt = forecasted_dt.replace(hour=0, minute=0)
        else:
            forecasted_dt = forecasted_dt.replace(minute=0)
        return forecasted_dt

    return _method
