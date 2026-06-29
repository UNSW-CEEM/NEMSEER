from datetime import datetime, timedelta
from typing import Tuple

from ..data import DATETIME_FORMAT
from ..downloader import _validate_forecast_type
from ..query import _dt_converter
from .validators import (
    _determine_last_market_day_end_for_half_hourly,
    validate_MTPASA_datetime_inputs,
    validate_P5MIN_datetime_inputs,
    validate_PREDISPATCH_datetime_inputs,
    validate_STPASA_datetime_inputs,
)


def _determine_valid_earliest_forecasted_for_pd(run_dt: datetime) -> datetime:
    """Determine the earliest forecasted time covered by a provided `run` time.

    For :term:`PREDISPATCH` and :term:`PDPASA`, a 1300 forecast run covers intervals
    from now to the end of the next trading day. The earliest forecasted time is
    therefore the first interval following the run.

    Args:
        run_dt: A `run` time.
    Returns:
        The earliest forecasted datetime covered by the given run.
    """
    return run_dt


def _determine_valid_latest_forecasted_for_pd(run_dt: datetime) -> datetime:
    """Determine the latest forecasted time covered by a provided `run` time.

    For :term:`PREDISPATCH` and :term:`PDPASA`, a given run covers intervals up to the
    end of the next trading day (i.e. 0400 two days after the run date).

    Args:
        run_dt: A `run` time.
    Returns:
        The latest forecasted datetime covered by the given run.
    """
    return _determine_last_market_day_end_for_half_hourly(run_dt)


def _determine_valid_earliest_forecasted_for_stpasa(run_dt: datetime) -> datetime:
    """Determine the earliest forecasted time covered by a provided :term:`STPASA`
    `run` time.

    :term:`STPASA` forecasts begin after the :term:`PREDISPATCH`/:term:`PDPASA`
    horizon ends. The run at 1400 on a given day covers from ~0430 two days later.

    Args:
        run_dt: A `run` time.
    Returns:
        The earliest forecasted datetime covered by the given run.
    """
    return _determine_valid_latest_forecasted_for_pd(run_dt) + timedelta(minutes=30)


def _determine_valid_latest_forecasted_for_stpasa(run_dt: datetime) -> datetime:
    """Determine the latest forecasted time covered by a provided :term:`STPASA`
    `run` time.

    :term:`STPASA` runs cover a rolling ~7-day window. The run at 1400 covers up to
    7 trading days ahead.

    Args:
        run_dt: A `run` time.
    Returns:
        The latest forecasted datetime covered by the given run.
    """
    last_market_day_end = _determine_last_market_day_end_for_half_hourly(run_dt)
    latest_forecasted = last_market_day_end + timedelta(days=6)
    return latest_forecasted


def _generate_p5min_forecasted_times(
    run_start: datetime, run_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`forecasted_start` and latest :term:`forecasted_end`
    for a set of user-supplied :term:`run_start` and :term:`run_end` times.

    Calls validation function to ensure that user-supplied `run` times are valid.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
    Returns:
        Tuple of datetimes containing the widest range of possible `forecasted` times.
    """
    forecasted_start = run_start
    forecasted_end = run_end + timedelta(minutes=55)
    validate_P5MIN_datetime_inputs(run_start, run_end, forecasted_start, forecasted_end)
    return forecasted_start, forecasted_end


def _generate_predispatch_forecasted_times(
    run_start: datetime, run_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`forecasted_start` and latest :term:`forecasted_end`
    for a set of user-supplied :term:`run_start` and :term:`run_end` times.

    Calls validation function to ensure that user-supplied `run` times are valid.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
    Returns:
        Tuple of datetimes containing the widest range of possible `forecasted` times.
    """
    forecasted_start = _determine_valid_earliest_forecasted_for_pd(run_start)
    forecasted_end = _determine_valid_latest_forecasted_for_pd(run_end)
    validate_PREDISPATCH_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return forecasted_start, forecasted_end


def _generate_pdpasa_forecasted_times(
    run_start: datetime, run_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`forecasted_start` and latest :term:`forecasted_end`
    for a set of user-supplied :term:`run_start` and :term:`run_end` times.

    Calls validation function to ensure that user-supplied `run` times are valid.

    :term:`PDPASA` shares its run schedule with :term:`PREDISPATCH`, so the same
    inversion logic applies.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
    Returns:
        Tuple of datetimes containing the widest range of possible `forecasted` times.
    """
    return _generate_predispatch_forecasted_times(run_start, run_end)


def _generate_stpasa_forecasted_times(
    run_start: datetime, run_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`forecasted_start` and latest :term:`forecasted_end`
    for a set of user-supplied :term:`run_start` and :term:`run_end` times.

    Calls validation function to ensure that user-supplied `run` times are valid.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
    Returns:
        Tuple of datetimes containing the widest range of possible `forecasted` times.
    """
    forecasted_start = _determine_valid_earliest_forecasted_for_stpasa(run_start)
    forecasted_end = _determine_valid_latest_forecasted_for_stpasa(run_end)
    validate_STPASA_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return forecasted_start, forecasted_end


def _generate_mtpasa_forecasted_times(
    run_start: datetime, run_end: datetime
) -> Tuple[datetime, datetime]:
    """Generates the earliest :term:`forecasted_start` and latest :term:`forecasted_end`
    for a set of user-supplied :term:`run_start` and :term:`run_end` times.

    Calls validation function to ensure that user-supplied `run` times are valid.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
    Returns:
        Tuple of datetimes containing the widest range of possible `forecasted` times.
    """
    run_start = run_start.replace(hour=0, minute=0, second=0, microsecond=0)
    run_end = run_end.replace(hour=0, minute=0, second=0, microsecond=0)
    if run_end.month == 2 and run_end.day == 29:
        plus_two_years = run_end.replace(year=run_end.year + 2, day=28)
    else:
        plus_two_years = run_end.replace(year=run_end.year + 2)
    forecasted_end = plus_two_years + timedelta(days=16)

    forecasted_start = run_start + timedelta(days=1)
    validate_MTPASA_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return forecasted_start, forecasted_end


def generate_forecasted_times(
    run_start: str, run_end: str, forecast_type: str
) -> Tuple[str, str]:
    """For a particular :term:`forecast type`, generates the earliest
    :term:`forecasted_start` and the latest :term:`forecasted_end` that are covered by
    the supplied :term:`run times`.

    This is the inverse of :func:`nemseer.generate_runtimes`: given a window of run
    times, it returns the widest window of forecasted times that those runs could
    produce. Using the returned :term:`forecasted_start` and :term:`forecasted_end`
    with :func:`nemseer.compile_data` will ensure all forecasted intervals covered by
    the supplied runs are retained.

    N.B. These have been determined based on AEMO documentation and actual data. This
    may not be accurate for all :term:`forecast types`, e.g. :term:`MTPASA` which is
    not run at a fixed time.

    Examples:
        See :ref:`getting valid forecasted times for a set of run times \
        <quick_start:getting valid forecasted times for a set of run times>`.

    Args:
        run_start: The earliest run time to consider.
        run_end: The latest run time to consider.
        forecast_type: One of :data:`nemseer.forecast_types`
    Returns:
        Tuple of `nemseer`-valid string datetimes that correspond to valid `forecasted`
        times.
    Raises:
        ValueError: If supplied `run` times are invalid.
    """
    _validate_forecast_type(forecast_type)
    if run_start > run_end:
        raise ValueError(
            "Run end datetime must be greater than or equal to run start datetime."
        )
    generate_map = {
        "P5MIN": _generate_p5min_forecasted_times,
        "PREDISPATCH": _generate_predispatch_forecasted_times,
        "PDPASA": _generate_pdpasa_forecasted_times,
        "STPASA": _generate_stpasa_forecasted_times,
        "MTPASA": _generate_mtpasa_forecasted_times,
    }
    generate_func = generate_map[forecast_type]
    dt_run_start = _dt_converter(run_start)
    dt_run_end = _dt_converter(run_end)
    (forecasted_start, forecasted_end) = generate_func(dt_run_start, dt_run_end)
    return (
        forecasted_start.strftime(DATETIME_FORMAT),
        forecasted_end.strftime(DATETIME_FORMAT),
    )
