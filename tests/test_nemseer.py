import logging

import grequests  # type: ignore
import pytest
import requests

from nemseer import download_raw_data, forecast_types, get_tables
from nemseer.downloader import (
    _build_useragent_generator,
    _construct_sqlloader_forecastdata_url,
)


class TestDowloadRawData:
    def test_download_and_query_check(self, caplog, download_file_to_cache):
        query = download_file_to_cache
        caplog.set_level(logging.INFO)
        date_strformat = "%Y/%m/%d %H:%M"
        download_raw_data(
            query.run_start.strftime(date_strformat),
            query.run_end.strftime(date_strformat),
            query.forecasted_start.strftime(date_strformat),
            query.forecasted_end.strftime(date_strformat),
            query.forecast_type,
            query.tables,
            query.raw_cache,
        )
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "Query raw data already downloaded to" in record.msg
            ]
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
