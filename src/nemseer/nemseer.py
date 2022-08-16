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
    keep_csv: bool = False,
) -> None:
    """Downloads raw forecast data from NEMWeb MMSDM Historical Data SQLLoader

    Downloads raw forecast data and converts to parquet.

    Arguments:
        forecast_start: Forecasts made at or after this datetime are queried.
        forecast_end: Forecasts made before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retained.
        forecast_type: `MTPASA`, `STPASA`, `PDPASA`, `PREDISPATCH` or `P5MIN`.
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        raw_cache: Path to download files
    """
    loader = Loader.initialise(
        forecast_start=forecast_start,
        forecast_end=forecast_end,
        forecasted_start=forecasted_start,
        forecasted_end=forecasted_end,
        forecast_type=forecast_type,
        tables=tables,
        raw_cache=raw_cache,
    )
    if loader.check_data_in_cache():
        pass
    else:
        downloader = ForecastTypeDownloader.from_Loader(loader)
        downloader.download_csv()
        downloader.convert_to_parquet(keep_csv=keep_csv)
