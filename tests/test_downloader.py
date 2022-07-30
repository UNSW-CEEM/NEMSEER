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
            self.forecast_start,
            self.forecasted_end,
            "STPASA",
            "REGIONSOLUTION",
            raw_cache=cache,
        )

    def invalid_tables_loader(self, cache):
        return Loader.initialise(
            self.forecast_start,
            self.forecast_end,
            self.forecast_start,
            self.forecasted_end,
            "P5MIN",
            ["DISPATCHLOAD", "REGIONDISPATCHSUM"],
            raw_cache=cache,
        )

    def test_invalid_tables(self, tmp_path):
        with pytest.raises(ValueError):
            ForecastTypeDownloader.from_Loader(self.invalid_tables_loader(tmp_path))
