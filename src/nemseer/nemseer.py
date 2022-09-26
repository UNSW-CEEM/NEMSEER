from typing import Dict, List, Tuple, Union

import pandas as pd
import xarray as xr

from .data_compilers import DataCompiler
from .downloader import ForecastTypeDownloader
from .forecast_type.run_time_generators import generate_runtimes
from .query import Query


def _initiate_downloads_from_query(query: Query, keep_csv: bool = False) -> None:
    """Initiates download actions using :class:`nemseer.query.Query`
    Args:
        query: :class:`nemseer.query.Query`
    Returns:
        None
    """
    if query.check_all_raw_data_in_cache():
        pass
    else:
        downloader = ForecastTypeDownloader.from_Query(query)
        downloader.download_csv()
        downloader.convert_to_parquet(keep_csv=keep_csv)
    return None


def download_raw_data(
    forecast_type: str,
    tables: Union[str, List[str]],
    raw_cache: str,
    run_start: Union[str, None] = None,
    run_end: Union[str, None] = None,
    forecasted_start: Union[str, None] = None,
    forecasted_end: Union[str, None] = None,
    keep_csv: bool = False,
) -> None:
    """Downloads raw forecast data from NEMWeb MMSDM Historical Data SQLLoader

    Downloads raw forecast data. Accepts a datetime pair, which can be either of:

    1. :attr:`run_start` and :attr:`run_end`
    2. :attr:`forecasted_start` and :attr:`forecasted_end`

    Examples:
        See :ref:`downloading raw data examples <quick_start:downloading raw data>`.

    Arguments:
        forecast_type: One of :data:`nemseer.forecast_types`
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        raw_cache: Path to create or reuse as :term:`raw_cache`. Files are downloaded
            to this directory and cached data is maintained in the parquet format.
        run_start: Forecast runs at or after this datetime are queried. If supplied,
            must be included with :attr:`run_end`.
        run_end: Forecast runs before or at this datetime are queried. If supplied,
            must be included with :attr:`run_start`.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained. If supplied, must be included with
            :attr:`forecasted_end`.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retained. If supplied, must be included with
            :attr:`forecasted_start`.
        keep_csv: Default False. If True, downloaded csvs are retained in the
            :term:`raw_cache`.
    Raises:
        ValueError: If a valid pair of datetimes is not supplied, or if more than a
            valid pair of datetimes is supplied.
    """

    def _generate_other_datetime_pair(
        start: str,
        end: str,
        input_datetime_type: str,
        forecast_type: str,
    ) -> Tuple[str, str]:
        """Given forecasted times, generates runtimes and vice versa.

        Args:
            start: Start datetime.
            end: End datetime.
            input_datetime_type: Specified whether :attr:`start` and :attr:`end`
                correspond to 'run' or 'forecasted' datetimes
            forecast_type: One of :data:`nemseer.forecast_types`
        Returns:
            A tuple of datetime strings that correspond to the "other" set of datetimes.
        Raises:
            ValueError: If :attr:`input_datetime_type` does not correspond to 'run'
                or 'forecasted'
        """
        if input_datetime_type not in ("run", "forecasted"):
            raise ValueError("Input datetime type must be 'run' or 'forecasted'")
        if input_datetime_type == "forecasted":
            (other_start, other_end) = generate_runtimes(start, end, forecast_type)
        else:
            other_start = start
            other_end = start
        return other_start, other_end

    if run_start and run_end and not forecasted_start and not forecasted_end:
        forecasted_start, forecasted_end = _generate_other_datetime_pair(
            run_start, run_end, "run", forecast_type
        )
    elif forecasted_start and forecasted_end and not run_start and not run_end:
        run_start, run_end = _generate_other_datetime_pair(
            forecasted_start, forecasted_end, "forecasted", forecast_type
        )
    else:
        raise ValueError(
            "Provide both of run_start and run_end (and no forecasted times),"
            + " or both of forecasted_start and forecasted_end (and no run times)."
        )
    query = Query.initialise(
        run_start=run_start,
        run_end=run_end,
        forecasted_start=forecasted_start,
        forecasted_end=forecasted_end,
        forecast_type=forecast_type,
        tables=tables,
        raw_cache=raw_cache,
    )
    _initiate_downloads_from_query(query, keep_csv=keep_csv)


def compile_data(
    run_start: str,
    run_end: str,
    forecasted_start: str,
    forecasted_end: str,
    forecast_type: str,
    tables: Union[str, List[str]],
    raw_cache: str,
    processed_cache: Union[None, str] = None,
    data_format: str = "df",
) -> Union[Dict[str, pd.DataFrame], Dict[str, xr.Dataset], None]:
    """Compiles queried data from :attr:`raw_cache` and/or :attr:`processed_cache`.

    For each queried table, this function:

    1. If required, downloads raw forecast data for the table and converts to the
       requested data structure.
    2. Otherwise, compiles table data from either of or both of the caches.
    3. Applies user-requested filtering to :term:`run times` and
       :term:`forecasted times` to any raw data.


    If :attr:`data_format` = "df" (default), a :class:`pandas.DataFrame` is returned.
    Otherwise, if :attr:`data_format` = "xr", a :class:`xarray.Dataset` is returned.

    Examples:
        See :ref:`compiling data examples <quick_start:compiling data>`.

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
        raw_cache: Path to create or reuse as :term:`raw_cache`. Files are downloaded
            to this directory and cached data is maintained in the parquet format.
        processed_cache (optional): Path to build or reuse :term:`processed_cache`.
            Should be distinct from :attr:`raw_cache`
        data_format: Default is 'df', which returns :class:`pandas DataFrame`.
            Can also request 'xr', which returns :class:`xarray.Dataset`.
    """
    if data_format not in (fmts := ("df", "xr")):
        raise ValueError(f"Invalid data format. Formats include: {fmts}")
    query = Query.initialise(
        run_start=run_start,
        run_end=run_end,
        forecasted_start=forecasted_start,
        forecasted_end=forecasted_end,
        forecast_type=forecast_type,
        tables=tables,
        raw_cache=raw_cache,
        processed_cache=processed_cache,
    )
    query.find_table_queries_in_processed_cache(data_format=data_format)
    compiler = DataCompiler.from_Query(query)
    if compiler.raw_tables:
        _initiate_downloads_from_query(query, keep_csv=False)
        compiler.compile_raw_data(data_format=data_format)
    compiler.compile_processed_data(data_format=data_format)
    if compiler.processed_cache:
        compiler.write_to_processed_cache()
    data = compiler.compiled_data
    return data
