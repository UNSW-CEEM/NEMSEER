import logging
import pathlib

import pytest

from nemseer.downloader import (
    ForecastTypeDownloader,
    _construct_sqlloader_forecastdata_url,
    get_sqlloader_forecast_tables,
    get_sqlloader_years_and_months,
)
from nemseer.downloader_helpers.data import MMSDM_ARCHIVE_URL
from nemseer.query import Query


def test_standard_sqlloader_url():
    url = _construct_sqlloader_forecastdata_url(2021, 2, "STPASA", "REGIONSOLUTION")
    assert url == (
        MMSDM_ARCHIVE_URL
        + "2021/MMSDM_2021_02/MMSDM_Historical_Data_SQLLoader/DATA/"
        + "PUBLIC_DVD_STPASA_REGIONSOLUTION_202102010000.zip"
    )


def test_allmonths_available():
    years_months = get_sqlloader_years_and_months()
    test_index = int(len(years_months) / 2)
    all_months = list(range(1, 13))
    assert years_months[list(years_months.keys())[test_index]] == all_months


def test_tables_for_invalid_forecasttype(get_test_year_and_month):
    with pytest.raises(ValueError):
        get_sqlloader_forecast_tables(*get_test_year_and_month, "FAIL")


def test_table_fetch_for_p5min(get_test_year_and_month):
    p5tables = get_sqlloader_forecast_tables(*get_test_year_and_month, "P5MIN")
    assert set(p5tables) == set(
        [
            "CONSTRAINTSOLUTION",
            "CASESOLUTION",
            "REGIONSOLUTION",
            "UNITSOLUTION",
            "INTERCONNECTORSOLN",
        ]
    )


class TestForecastTypeDownloader:
    def valid_query(self, raw_cache, valid_datetimes):
        (
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
        ) = valid_datetimes
        return Query.initialise(
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
            "STPASA",
            "REGIONSOLUTION",
            raw_cache=raw_cache,
        )

    def valid_casesolution(self, raw_cache, valid_datetimes):
        (
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
        ) = valid_datetimes
        return Query.initialise(
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
            "STPASA",
            "CASESOLUTION",
            raw_cache=raw_cache,
        )

    def invalid_tables_query(self, raw_cache, valid_datetimes):
        (
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
        ) = valid_datetimes
        return Query.initialise(
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
            "P5MIN",
            ["DISPATCHLOAD", "REGIONDISPATCHSUM"],
            raw_cache=raw_cache,
        )

    def constraint_solution_query(self, raw_cache, valid_datetimes):
        (
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
        ) = valid_datetimes
        return Query.initialise(
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
            "P5MIN",
            "CONSTRAINTSOLUTION",
            raw_cache=raw_cache,
        )

    def casesolution_query(self, raw_cache, forecast_type, valid_datetimes):
        (
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
        ) = valid_datetimes
        return Query.initialise(
            forecast_start,
            forecast_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            "CASESOLUTION",
            raw_cache=raw_cache,
        )

    def test_invalid_tables(self, tmp_path, valid_datetimes):
        with pytest.raises(ValueError):
            ForecastTypeDownloader.from_Query(
                self.invalid_tables_query(tmp_path, valid_datetimes)
            )

    def test_table_enumeration(self, tmp_path, valid_datetimes):
        """
        Add other initialisations if additional tables require enumeration
        """
        ftd = ForecastTypeDownloader.from_Query(
            self.constraint_solution_query(tmp_path, valid_datetimes)
        )
        to_check = set(
            [
                "CONSTRAINTSOLUTION1",
                "CONSTRAINTSOLUTION2",
                "CONSTRAINTSOLUTION3",
                "CONSTRAINTSOLUTION4",
            ]
        )
        assert to_check.issubset(set(ftd.tables))

    def test_casesolution_download_and_to_parquet(self, tmp_path, valid_datetimes):
        for forecast_type in ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA"):
            query = self.casesolution_query(tmp_path, forecast_type, valid_datetimes)
            downloader = ForecastTypeDownloader.from_Query(query)
            downloader.download_csv()
            downloader.convert_to_parquet()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 5
        assert all([True for file in path.iterdir() if "CASESOLUTION" in file.name])
        assert all([True for file in path.iterdir() if ".parquet" in file.name])

    def test_skip_existing_component_of_query(self, caplog, download_file_to_cache):
        query = download_file_to_cache
        query.tables.append("CASESOLUTION")
        downloader = ForecastTypeDownloader.from_Query(query)
        caplog.set_level(logging.INFO)
        downloader.download_csv()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "REGIONRESULT for 2/2021 in raw_cache" == record.msg
            ]
        )

    def test_parquet_conversion(self, caplog, tmp_path, valid_datetimes):
        downloader = ForecastTypeDownloader.from_Query(
            self.valid_casesolution(tmp_path, valid_datetimes)
        )
        caplog.set_level(logging.INFO)
        downloader.download_csv()
        downloader.convert_to_parquet(keep_csv=True)
        downloader.convert_to_parquet()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "PUBLIC_DVD_STPASA_CASESOLUTION_202102010000.parquet already exists"
                == record.msg
            ]
        )
