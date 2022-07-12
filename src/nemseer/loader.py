import os

from attrs import define, field, validators
from datetime import datetime
from .downloader import _get_mmsdm_tables_for_yearmonths
from typing import Dict, List, Optional, Union


def _dt_converter(value: str) -> datetime:
    """Convert string to datetime.

    Args:
        value: String with format %d/%m/%Y %H:%M
    Returns:
        Datetime object
    """
    try:
        format = "%d/%m/%Y %H:%M"
        return datetime.strptime(value, format)
    except ValueError:
        raise ValueError(
            "Datetime should be provided as follows: dd/mm/yyyy hh:mm"
            )


def _tablestr_converter(value: Union[str, List[str]]) -> List[str]:
    """Returns a list of table strings, even if a single string is provided

    Args:
        value: Table string or list of table strings
    Returns:
        List of strings
    """
    if type(value) is str:
        return [value]
    else:
        return list(value)


def _validate_forecast_chronology(instance, attribute, value):
    """Validates forecast_start against forecast_end"""
    if instance.forecast_end < value:
        raise ValueError(
            "Forecast end datetime must be greater than or equal to"
            + " forecast start datetime.")


def _validate_forecasted_chronology(instance, attribute, value):
    """Validated forecasted_start against forecasted_end"""
    if instance.forecasted_end < value:
        raise ValueError(
            "Forecasted end datetime must be greater than or equal to"
            + " forecasted start datetime.")


def _validate_forecast_forecasted_chronology(instance, attribute, value):
    """Validates forecast_start against forecasted_start"""
    if instance.forecasted_start <= value:
        raise ValueError(
            "Forecasted start datetime should be after forecast"
            + " start datetime."
        )


def _validate_tables_on_forecast_start(instance, attribute, value):
    """Validates tables for the provided forecast type.

    Checks user-supplied tables against tables available in MMS Historical
    Data SQL Loader for the month and year of forecast_start.
    """
    start_dt = instance.forecast_start
    tables = _get_mmsdm_tables_for_yearmonths(start_dt.year, start_dt.month,
                                              instance.forecast_type)
    if not set(value).issubset(set(tables)):
        raise ValueError(
            "Table not available from MMS Historical Data SQL Loader"
            + f" (for {start_dt.month}/{start_dt.year}).\n"
            + f"Tables include: {tables}"
        )


def _validate_path(instance, attribute, value):
    """Check the path exists."""
    if not os.path.exists(value):
        raise ValueError(
            f"{attribute.name} supplied ('{value}') is invalid."
        )


@define
class Loader:
    """`Loader` validates user inputs and dispatches data fetchers.

    Construct `Loader` using the `Loader.initialise()` constructor. This
    ensures query metadata is constructed approriately.

    Loader:

    - Validates user input data
        - Checks datetime are dd/mm/yyyy HH:MM
        - Checks datetime chronology (e.g. end is after start)
        - Validates `forecast_type`
        - Validates user-supplied tables against what is available on NEMWeb
    - Retains query metadata (via constructor class method `initialise`)
    - Can dispatch various Managers and Downloaders

    Attributes:
        forecast_start: Forecasts made at or after this datetime are queried.
        forecast_end: Forecasts made before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
        forecast_type: `MTPASA`, `STPASA`, `PDPASA`, `PREDISPATCH` or `P5MIN`.
        tables: Table or tables required. A single table can be supplied as 
            a string. Multiple tables can be supplied as a list of strings.
        metadata: Metadata dictionary. Constructed by `Loader.initialise()`.
        raw_cache (optional): Path to build or reuse raw cache.
        processed_cache (optional): Path to build or reuse processed cache.

    """
    forecast_start: str = field(converter=_dt_converter,
                                validator=[
                                    _validate_forecast_chronology,
                                    _validate_forecast_forecasted_chronology
                                    ])
    forecast_end: str = field(converter=_dt_converter)
    forecasted_start: str = field(converter=_dt_converter,
                                  validator=_validate_forecasted_chronology)
    forecasted_end: str = field(converter=_dt_converter)
    forecast_type: str = field(validator=validators.in_(
        ['MTPASA', 'STPASA', 'PDPASA', 'PREDISPATCH', 'P5MIN']
        ))
    tables: Union[str, List[str]] = field(
        converter=_tablestr_converter,
        validator=_validate_tables_on_forecast_start)
    metadata: Dict
    raw_cache: Optional[str] = field(
        default=None, validator=validators.optional(_validate_path)
        )
    processed_cache: Optional[str] = field(
        default=None, validator=validators.optional(_validate_path)
    )

    @classmethod
    def initialise(cls, forecast_start: str, forecast_end: str,
                   forecasted_start: str, forecasted_end: str,
                   forecast_type: str, tables: Union[str, List[str]],
                   raw_cache: Optional[str] = None,
                   processed_cache: Optional[str] = None) -> "Loader":
        """Constructor method for Loader. Assembles query metatdata.

        """
        metadata = {
            "forecast_start": forecast_start, "forecast_end": forecast_end,
            "forecasted_start": forecasted_start,
            "forecasted_end": forecasted_end, "forecast_type": forecast_type,
            "tables": tables
        }
        return cls(forecast_start=forecast_start, forecast_end=forecast_end,
                   forecasted_start=forecasted_start,
                   forecasted_end=forecasted_end, forecast_type=forecast_type,
                   tables=tables, metadata=metadata, raw_cache=raw_cache,
                   processed_cache=processed_cache)
