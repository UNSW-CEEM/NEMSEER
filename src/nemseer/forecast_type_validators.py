from datetime import datetime, timedelta

_PRINT_FORMAT = "%Y/%m/%d %H:%S"


def validate_P5MIN_datetime_inputs(
    forecast_start: datetime,
    forecast_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `P5MIN` forecast datetime inputs

    From `AEMO MMS Data Model Report <https://nemweb.com.au/Reports/Current/
    MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_230.htm#1>`_:

      The 5-minute Predispatch cycle runs every 5-minutes to produce a dispatch and
      pricing schedule to a 5-minute resolution covering the next hour,
      a total of twelve periods.

    Validation checks:

    1. Minute component of datetime inputs is on a 5 minute basis
    2. :attr:`forecasted_end` is not more than 55 minutes (12 cycles) from
    :attr:`forecast_end`

    These 12 dispatch cycles include the immediate interval
    (i.e. where `RUN_DATETIME` = `INTERVAL_DATETIME`)

    Args:
        forecast_start: Forecast runs at or after this datetime are queried.
        forecast_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    acceptable_minutes = set(range(0, 60, 5))
    for dt_input in (forecast_start, forecast_end, forecasted_start, forecasted_end):
        if dt_input.minute not in acceptable_minutes:
            raise ValueError(
                "P5MIN is run every 5 minutes.\n"
                + " Minutes in datetime inputs should correspond to: "
                + f"{acceptable_minutes}"
            )
    if forecasted_end > (allowed := forecast_end + timedelta(minutes=55)):
        print_allowed = allowed.strftime(_PRINT_FORMAT)
        raise ValueError(
            "For P5MIN, forecasted_end must be within 55 minutes of forecast_end.\n"
            + f"This corresponds to {print_allowed} for the provided forecast_end"
        )
    return None


def validate_PREDISPATCH_datetime_inputs(
    forecast_start: datetime,
    forecast_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `PREDISPATCH` forecast datetime inputs

    From `AEMO Pre-dispatch SOP <https://www.aemo.com.au/-/media/files/electricity/nem/
    security_and_reliability/power_system_ops/procedures/
    so_op_3704-predispatch.pdf?la=en>`_:

      Currently AEMO runs pre-dispatch every half hour, on the half hour for each
      30-minute period up to and including the last 30-minute period of the last trading
      day for which bid band prices have closed. As changes to bid band prices for the
      next trading day close at 1230 hours EST, AEMO will at 1230 hours,
      publish pre-dispatch for all 30-minute periods up to the end of the
      next trading day.

    Noting that:

    - A market/trading day extends from 0400 to 0400 on the next day.
    - Pre-dispatch executed at 1230 hours is associated with the 1300 hours run time.
      That is, `PREDISPATCHSEQ` corresponding to 13:00 contains bids for the
      next trading day.

    Validation checks:

    1. Minute component of datetime inputs is on a 30 minute basis
    2. :attr:`forecasted_end` is no later than the end of the last trading day for which
    bid band prices have closed (the end of that day being 04:00) by
    :attr:`forecast_end`

    Args:
        forecast_start: Forecast runs at or after this datetime are queried.
        forecast_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    acceptable_minutes = set((0, 30))
    for dt_input in (forecast_start, forecast_end, forecasted_start, forecasted_end):
        if dt_input.minute not in acceptable_minutes:
            raise ValueError(
                "PREDISPATCH is run every 30 minutes.\n"
                + " Minutes in datetime inputs should correspond to: "
                + f"{acceptable_minutes}"
            )
    if forecast_end.hour >= 13:
        check_date = (forecast_end + timedelta(days=2)).date()
    else:
        check_date = (forecast_end + timedelta(days=1)).date()
    check_dt = datetime(
        year=check_date.year,
        month=check_date.month,
        day=check_date.day,
        hour=4,
        minute=0,
    )
    if forecasted_end > check_dt:
        print_allowed = check_dt.strftime(_PRINT_FORMAT)
        raise ValueError(
            f"For PREDISPATCH, forecasted_end must be no later than {print_allowed} "
            + "based on the supplied forecast_end"
        )
    return None


def validate_PDPASA_datetime_inputs(
    forecast_start: datetime,
    forecast_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `PDPASA` forecast datetime inputs

    Points to :func:`validate_PREDISPATCH_datetime_inputs()` as validation for
    PREDISPATCH and PDPASA are the same.

    Args:
        forecast_start: Forecast runs at or after this datetime are queried.
        forecast_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    validate_PREDISPATCH_datetime_inputs(
        forecast_start, forecast_end, forecasted_start, forecasted_end
    )
    return None


def validate_STPASA_inputs():
    """
    .. todo:: Create `STPASA` validator
    """
    return None


def validate_MTPASA_inputs():
    """
    .. todo:: Create `MTPASA` validator
    .. todo:: Handle MTPASA DUID Availability
    """
    return None
