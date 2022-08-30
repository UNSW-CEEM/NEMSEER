import grequests  # type: ignore
import pytest
import requests

from nemseer import forecast_types, get_tables
from nemseer.downloader import (
    _build_useragent_generator,
    _construct_sqlloader_forecastdata_url,
)


@pytest.mark.parametrize("ftype", forecast_types)
class TestAllTableRequests:
    def test_all_table_requests_valid(self, ftype, get_test_year_and_month):
        def _check_size(response: requests.Response):
            size = int(response.headers.get("Content-Length", 0))
            assert size > 100

        year, month = get_test_year_and_month
        ftype_tables = get_tables(year, month, ftype)
        useragents = _build_useragent_generator(len(ftype_tables))
        reqs = []
        for table in ftype_tables:
            url = _construct_sqlloader_forecastdata_url(year, month, ftype, table)
            reqs.append(grequests.get(url, headers={"User-Agent": next(useragents)}))
        for resp in grequests.imap(reqs, size=len(reqs)):
            _check_size(resp)
