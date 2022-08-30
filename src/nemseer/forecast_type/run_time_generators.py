from datetime import datetime, timedelta
from typing import Tuple

from ..data import DATETIME_FORMAT
from ..downloader import _validate_forecast_type
from ..query import _dt_converter
from .validators import (
    validate_MTPASA_datetime_inputs,
    validate_P5MIN_datetime_inputs,
    validate_PREDISPATCH_datetime_inputs,
    validate_STPASA_datetime_inputs,
)


def _determine_valid_earliest_run_for_PD(forecasted_dt: datetime) -> datetime:
    """Determine the earliest forecast run to use for a provided `forecasted` time

    For :term:`PREDISPATCH` and :term:`PDPASA` the 1300 forecast run will
    extend out to the last relevant interval of the trading day for which bid band price
    submission closed at 1230.

    Args:
        dt: A `forecasted` time.
    Returns:
        A 1300 run time, corresponding to the earliest possible run.

    """
    if forecasted_dt.hour > 4 or (forecasted_dt.hour == 4 and forecasted_dt.minute > 0):
        run_1300 = forecasted_dt - timedelta(days=1)
    else:
        run_1300 = forecasted_dt - timedelta(days=2)
    return run_1300.replace(hour=13, minute=0)


def _determine_valid_latest_run_for_STPASA(forecasted_dt: datetime) -> datetime:
    """Determines (one of the) latest forecast runs to use for a provided `forecasted`
    time

    :term:`STPASA` runs will produce forecasts that begin after the end of the
    `PREDISPATCH`/`PDPASA` forecast horizon.

    Prior to the change in the frequency at which ST PASA is run, 14:00 would be the
    latest forecast time. This has since changed to 13:00 (as ST PASA is now run
    hourly). To ensure "backwards-compatability", this function returns a run at 14:00.

    Args:
        dt: A `forecasted` time.
    Returns:
        (One of the) earliest possible run times.

    """
    if forecasted_dt.hour > 4 or (forecasted_dt.hour == 4 and forecasted_dt.minute > 0):
        run_1400 = forecasted_dt - timedelta(days=1)
    else:
        run_1400 = forecasted_dt - timedelta(days=2)
    return run_1400.replace(hour=14, minute=0)


def generate_P5MIN_runtimes(
    forecasted_start: datetime, forecasted_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`run_start` and latest :term:`run_end` for a set of
    user-supplied :term:`forecasted_start` and :term:`forecaseted_end` times.

    Calls validation function to ensure that user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Returns:
        Tuple of datetimes containing  the widest range of possible `forecasted` times
    """
    run_start = forecasted_start - timedelta(minutes=55)
    run_end = forecasted_end
    validate_P5MIN_datetime_inputs(run_start, run_end, forecasted_start, forecasted_end)
    return (run_start, run_end)


def generate_PREDISPATCH_runtimes(
    forecasted_start: datetime, forecasted_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`run_start` and latest :term:`run_end` for a set of
    user-supplied :term:`forecasted_start` and :term:`forecaseted_end` times.

    Calls validation function to ensure that user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Returns:
        Tuple of datetimes containing  the widest range of possible `forecasted` times
    """
    run_start = _determine_valid_earliest_run_for_PD(forecasted_start)
    run_end = forecasted_end
    validate_PREDISPATCH_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return (run_start, run_end)


def generate_PDPASA_runtimes(
    forecasted_start: datetime, forecasted_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`run_start` and latest :term:`run_end` for a set of
    user-supplied :term:`forecasted_start` and :term:`forecaseted_end` times.

    Calls validation function to ensure that user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Returns:
        Tuple of datetimes containing  the widest range of possible `forecasted` times
    """

    (run_start, run_end) = generate_PREDISPATCH_runtimes(
        forecasted_start, forecasted_end
    )
    return (run_start, run_end)


def generate_STPASA_runtimes(
    forecasted_start: datetime, forecasted_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`run_start` and latest :term:`run_end` for a set of
    user-supplied :term:`forecasted_start` and :term:`forecaseted_end` times.

    Calls validation function to ensure that user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Returns:
        Tuple of datetimes containing  the widest range of possible `forecasted` times
    """
    run_start = _determine_valid_latest_run_for_STPASA(forecasted_start) - timedelta(
        days=6
    )
    run_end = _determine_valid_latest_run_for_STPASA(forecasted_end)
    validate_STPASA_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return (run_start, run_end)


def generate_MTPASA_runtimes(
    forecasted_start: datetime, forecasted_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`run_start` and latest :term:`run_end` for a set of
    user-supplied :term:`forecasted_start` and :term:`forecaseted_end` times.

    Calls validation function to ensure that user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Returns:
        Tuple of datetimes containing  the widest range of possible `forecasted` times
    """
    if forecasted_start.month == 2 and forecasted_start.day == 29:
        minus_two_years = forecasted_start.replace(
            year=forecasted_start.year - 2, day=28
        )
    else:
        minus_two_years = forecasted_start.replace(year=forecasted_start.year - 2)
    run_start = minus_two_years - timedelta(days=16)
    run_end = forecasted_end - timedelta(days=6)
    validate_MTPASA_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return (run_start, run_end)


def generate_runtimes(
    forecasted_start: str, forecasted_end: str, forecast_type: str
) -> Tuple[str, str]:
    """For a particular :term:`forecast type`, generates valid `run` times provided that
    user-supplied `forecasted` times are valid.

    Args:
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retained.
        forecast_type: One of :data:`nemseer.forecast_types`
    Returns:
        Tuple of `nemseer`-valid string datetimes that correspond to valid `run` times
    Raises:
        ValueError: If supplied `forecasted` times are invalid.
    """
    _validate_forecast_type(forecast_type)
    if forecasted_start > forecasted_end:
        raise ValueError(
            "Forecasted end datetime must be greater than or equal to"
            + " forecasted start datetime."
        )
    generate_map = {
        "P5MIN": generate_P5MIN_runtimes,
        "PREDISPATCH": generate_PREDISPATCH_runtimes,
        "PDPASA": generate_PDPASA_runtimes,
        "STPASA": generate_STPASA_runtimes,
        "MTPASA": generate_MTPASA_runtimes,
    }
    generate_func = generate_map[forecast_type]
    (run_start, run_end) = generate_func(
        _dt_converter(forecasted_start), _dt_converter(forecasted_end)
    )
    return (
        run_start.strftime(DATETIME_FORMAT),
        run_end.strftime(DATETIME_FORMAT),
    )
