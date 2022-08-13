import pathlib

import pytest

from nemseer.downloader import ForecastTypeDownloader, _enumerate_tables
from nemseer.loader import Loader


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

    def test_casesolution_zip_download(self, tmp_path):
        for forecast_type in ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA"):
            loader = self.casesolution_loader(tmp_path, forecast_type)
            downloader = ForecastTypeDownloader.from_Loader(loader)
            downloader.download_zip()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 5
        assert all([True for file in path.iterdir() if "CASESOLUTION" in file.name])
