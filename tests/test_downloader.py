import pathlib

import pytest

from nemseer.downloader import (
    ForecastTypeDownloader,
    _construct_sqlloader_forecastdata_url,
    _enumerate_tables,
    get_sqlloader_forecast_tables,
    get_sqlloader_years_and_months,
)
from nemseer.downloader_helpers.data import MMSDM_ARCHIVE_URL
from nemseer.loader import Loader


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


def test_enumerate_tables():
    tables = ["REGIONDISPATCH", "DISPATCHLOAD", "testing"]
    table_str = "testing"
    assert _enumerate_tables(tables, table_str, 2) == [
        "REGIONDISPATCH",
        "DISPATCHLOAD",
        "testing1",
        "testing2",
    ]


class TestForecastTypeDownloader:
    forecast_start = "01/02/2021 00:00"
    forecast_end = "05/02/2021 00:00"
    forecasted_start = "08/02/2021 00:00"
    forecasted_end = "08/02/2021 23:55"

    def valid_loader(self, cache):
        return Loader.initialise(
            self.forecast_start,
            self.forecast_end,
            self.forecasted_start,
            self.forecasted_end,
            "STPASA",
            "REGIONSOLUTION",
            raw_cache=cache,
        )

    def invalid_tables_loader(self, cache):
        return Loader.initialise(
            self.forecast_start,
            self.forecast_end,
            self.forecasted_start,
            self.forecasted_end,
            "P5MIN",
            ["DISPATCHLOAD", "REGIONDISPATCHSUM"],
            raw_cache=cache,
        )

    def constraint_solution_loader(self, cache):
        return Loader.initialise(
            self.forecast_start,
            self.forecast_end,
            self.forecasted_start,
            self.forecasted_end,
            "P5MIN",
            "CONSTRAINTSOLUTION",
            raw_cache=cache,
        )

    def casesolution_loader(self, cache, forecast_type):
        return Loader.initialise(
            self.forecast_start,
            self.forecast_end,
            self.forecasted_start,
            self.forecasted_end,
            forecast_type,
            "CASESOLUTION",
            raw_cache=cache,
        )

    def test_invalid_tables(self, tmp_path):
        with pytest.raises(ValueError):
            ForecastTypeDownloader.from_Loader(self.invalid_tables_loader(tmp_path))

    def test_table_enumeration(self, tmp_path):
        """
        Add other initialisations if additional tables require enumeration
        """
        ftd = ForecastTypeDownloader.from_Loader(
            self.constraint_solution_loader(tmp_path)
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

    def test_casesolution_download_and_to_parquet(self, tmp_path):
        for forecast_type in ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA"):
            loader = self.casesolution_loader(tmp_path, forecast_type)
            downloader = ForecastTypeDownloader.from_Loader(loader)
            downloader.download_csv()
            downloader.convert_to_parquet()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 5
        assert all([True for file in path.iterdir() if "CASESOLUTION" in file.name])
        assert all([True for file in path.iterdir() if ".parquet" in file.name])
