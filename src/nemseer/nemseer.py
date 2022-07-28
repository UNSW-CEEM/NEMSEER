from typing import List, Union

from .downloader import ForecastTypeDownloader
from .loader import Loader


def download_raw_data(
    forecast_start: str,
    forecast_end: str,
    forecasted_start: str,
    forecasted_end: str,
    forecast_type: str,
    tables: Union[str, List[str]],
    raw_cache: str,
) -> None:
    loader = Loader.initialise(
        forecast_start=forecast_start,
        forecast_end=forecast_end,
        forecasted_start=forecasted_start,
        forecasted_end=forecasted_end,
        forecast_type=forecast_type,
        tables=tables,
        raw_cache=raw_cache,
    )
    downloader = ForecastTypeDownloader.from_Loader(loader)
    downloader.download_zip()
