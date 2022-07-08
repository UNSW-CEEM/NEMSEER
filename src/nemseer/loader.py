from attrs import define, field, validators
from datetime import datetime
from nemseer.downloader import _get_mmsdm_tables_for_yearmonths
from typing import Dict, List


def _dt_converter(value: str) -> datetime:
    """Convert string to datetime.

    Args:
        value: String with format YYYY/MM/DD
    Returns:
        Datetime object
    """
    format = "%Y/%m/%d %H:%M:%S"
    return datetime.strptime(value, format)


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
    """
    Checks user-supplied tables against tables available in MMS Historical
    Data SQL Loader for the month and year of forecast_start.
    """
    start_dt = instance.forecast_start
    tables = _get_mmsdm_tables_for_yearmonths(start_dt.year, start_dt.month,
                                              instance.forecast_type)
    if not set(value).issubset(set(tables)):
        raise ValueError(
            "Table not available from MMS Historical Data SQL Loader"
            + f"for {start_dt.month}/{start_dt.year}.\n"
            + f"Tables include: {tables}"
        )


@define
class DataLoader:
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
    tables: List[str] = field(validator=_validate_tables_on_forecast_start)
    metadata: Dict

    @classmethod
    def initialise(cls, forecast_start: str, forecast_end: str,
                   forecasted_start: str, forecasted_end: str,
                   forecast_type: str, tables: List[str]) -> "DataLoader":
        metadata = {
            "forecast_start": forecast_start, "forecast_end": forecast_end,
            "forecasted_start": forecasted_start,
            "forecasted_end": forecasted_end, "forecast_type": forecast_type,
            "tables": tables
        }
        return cls(forecast_start=forecast_start, forecast_end=forecast_end,
                   forecasted_start=forecasted_start,
                   forecasted_end=forecasted_end, forecast_type=forecast_type,
                   tables=tables, metadata=metadata)
