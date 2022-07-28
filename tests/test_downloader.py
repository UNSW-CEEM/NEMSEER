from datetime import datetime

import pytest

from nemseer.downloader import ForecastTypeDownloader


def test_invalid_tables():
    """
    # TODO: Put under class for testing
    # TODO: Create Loader fixture for testing ForecastTypeDownloader
    """
    with pytest.raises(ValueError):
        same_forecast_dates = [
            datetime.strptime("01/02/2021 02:03", "%d/%m/%Y %H:%M"),
            datetime.strptime("01/02/2021 02:03", "%d/%m/%Y %H:%M"),
        ]
        ForecastTypeDownloader(
            forecast_start=same_forecast_dates[0],
            forecast_end=same_forecast_dates[1],
            forecast_type="P5MIN",
            tables=["DISPATCHLOAD", "REGIONDISPATCHSUM"],
        )
