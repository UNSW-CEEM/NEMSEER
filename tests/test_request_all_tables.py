import logging

import pytest
import requests
from requests_futures.sessions import FuturesSession

from nemseer import forecast_types, get_tables
from nemseer.downloader import (
    _build_useragent_generator,
    _construct_sqlloader_forecastdata_url,
)

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("ftype", forecast_types)
class TestAllTableRequests:
    def test_all_table_requests_valid(self, ftype, get_test_year_and_month):
        def _check_size(response: requests.Response):
            size = int(response.headers.get("Content-Length", 0))
            if size < 100:
                logger.warning(
                    f"{size=} for {ftype=} {response.url=} {response.status_code=} "
                )
            assert size > 100

        year, month = get_test_year_and_month
        ftype_tables = get_tables(year, month, ftype)
        useragents = _build_useragent_generator(len(ftype_tables))
        with FuturesSession(max_workers=len(ftype_tables)) as session:
            futures = [
                session.get(url, headers={"User-Agent": next(useragents)})
                for url in [
                    _construct_sqlloader_forecastdata_url(year, month, ftype, table)
                    for table in ftype_tables
                ]
            ]
            for future in futures:
                resp = future.result()
                _check_size(resp)
