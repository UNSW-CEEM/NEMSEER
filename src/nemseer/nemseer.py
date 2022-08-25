from typing import List, Union

from .downloader import ForecastTypeDownloader
from .query import Query


def download_raw_data(
    run_start: str,
    run_end: str,
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
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retained.
        forecast_type: One of :data:`nemseer.forecast_types`
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        raw_cache: Path to download files
    """
    query = Query.initialise(
        run_start=run_start,
        run_end=run_end,
        forecasted_start=forecasted_start,
        forecasted_end=forecasted_end,
        forecast_type=forecast_type,
        tables=tables,
        raw_cache=raw_cache,
    )
    if query.check_data_in_cache():
        pass
    else:
        downloader = ForecastTypeDownloader.from_Query(query)
        downloader.download_csv()
        downloader.convert_to_parquet(keep_csv=keep_csv)
