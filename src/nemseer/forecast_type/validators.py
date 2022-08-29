from datetime import datetime, timedelta

from nemseer.data import DATETIME_FORMAT


def _determine_last_market_day_end_for_half_hourly(dt: datetime) -> datetime:
    """Returns end of last trading day for which price offer submission has closed by
    the supplied datetime.

    Only valid for forecasts datetimes with half-hourly increments, and that are run
    at or less frequently than every half hour.

    Args:
        dt: Datetime to find end of next
    Returns:
        Datetime corresponding to end of the last trading day for which price offer
        submission has closed by the supplied datetime.
    """
    if dt.hour >= 13:
        end_date = (dt + timedelta(days=2)).date()
    else:
        end_date = (dt + timedelta(days=1)).date()
    end_dt = datetime(
        year=end_date.year,
        month=end_date.month,
        day=end_date.day,
        hour=4,
        minute=0,
    )
    return end_dt


def validate_P5MIN_datetime_inputs(
    run_start: datetime,
    run_end: datetime,
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

    Check 1:
      Minute component of datetime inputs is on a 5 minute basis
    Check 2:
      :attr:`forecasted_end` is not more than 55 minutes (12 cycles) from
      :attr:`run_end`

    These 12 dispatch cycles include the immediate interval
    (i.e. where `RUN_DATETIME` = `INTERVAL_DATETIME`)

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    # Check 1
    acceptable_minutes = set(range(0, 60, 5))
    for dt_input in (run_start, run_end, forecasted_start, forecasted_end):
        if dt_input.minute not in acceptable_minutes:
            raise ValueError(
                "P5MIN is run every 5 minutes.\n"
                + "Minutes in datetime inputs should correspond to: "
                + f"{acceptable_minutes}"
            )
    # Check 2
    if forecasted_end > (allowed := run_end + timedelta(minutes=55)):
        print_allowed = allowed.strftime(DATETIME_FORMAT)
        raise ValueError(
            "For P5MIN, forecasted_end must be within 55 minutes of run_end.\n"
            + f"This corresponds to {print_allowed} for the provided run_end"
        )
    return None


def validate_PREDISPATCH_datetime_inputs(
    run_start: datetime,
    run_end: datetime,
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

    Check 1:
      Minute component of datetime inputs is on a 30 minute basis
    Check 2:
      :attr:`forecasted_end` is no later than the end of the last trading day for which
      bid band prices have closed (the end of that day being 04:00) by
      :attr:`run_end`

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    # Check 1
    acceptable_minutes = set((0, 30))
    for dt_input in (run_start, run_end, forecasted_start, forecasted_end):
        if dt_input.minute not in acceptable_minutes:
            raise ValueError(
                "PREDISPATCH/PDPASA is run every 30 minutes.\n"
                + "Minutes in datetime inputs should correspond to: "
                + f"{acceptable_minutes}"
            )
    # Check 2
    check_dt = _determine_last_market_day_end_for_half_hourly(run_end)
    if forecasted_end > check_dt:
        print_allowed = check_dt.strftime(DATETIME_FORMAT)
        raise ValueError(
            "For PREDISPATCH/PDPASA, forecasted_end must be no later than"
            + f" {print_allowed} based on the supplied run_end"
        )
    return None


def validate_PDPASA_datetime_inputs(
    run_start: datetime,
    run_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `PDPASA` forecast datetime inputs

    Points to :func:`validate_PREDISPATCH_datetime_inputs()` as validation for
    PREDISPATCH and PDPASA are the same.

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    validate_PREDISPATCH_datetime_inputs(
        run_start, run_end, forecasted_start, forecasted_end
    )
    return None


def validate_STPASA_datetime_inputs(
    run_start: datetime,
    run_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `STPASA` forecast datetime inputs

    From `AEMO PASA Outputs <https://aemo.com.au/energy-systems/electricity/
    national-electricity-market-nem/data-nem/market-management-system-mms-data/
    projected-assessment-of-system-adequacy-pasa>`_:

      [ST PASA] is published every 2 hours and provides detailed disclosure of
      short-term is published every 2 hours and provides detailed disclosure of
      short-term power-system supply/demand balance prospects for six days
      following the next trading day. The information is provided for each half-hour
      within the report period

    Noting that:

    - A market/trading day extends from 0400 to 0400 on the next day.
    - `ST PASA` is the "reverse" of `PREDISPATCH`
      - `ST PASA` **starts** after the end of the next trading day for which bids have
      been submitted

    The National Electricity Rules and some of AEMO's procedures state that ST PASA
    is run every two hours. The frequency was increased to hourly. See
    `Spot Market Operations Timetable <https://www.aemo.com.au/-/media/Files/
    Electricity/NEM/Security_and_Reliability/Dispatch/
    Spot-Market-Operations-Timetable.pdf>`_.


    Validation checks:

    Check 1:
      Minute component of forecast datetimes is on an hourly basis (i.e. 0 minutes)
    Check 2:
      Minute component of forecasted datetimes is on a 30 minute basis
    Check 3:
      :attr:`forecasted_start` is not equal to or earlier than the end of the
      last trading day for which bid band prices have closed
      (the end of that day being 04:00) by :attr:`run_start`
    Check 4:
      :attr:`forecasted_end` is no later than 6 days from the end of the last trading
      day for which bid band prices have closed by :attr:`run_end`

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    # Check 1
    for run_input in (run_start, run_end):
        if run_input.minute != 0:
            raise ValueError("ST PASA run_start and run_end must be on the hour")
    # Check 2
    forecasted_minutes = set((0, 30))
    for dt_input in (forecasted_start, forecasted_end):
        if dt_input.minute not in forecasted_minutes:
            raise ValueError(
                "ST PASA forecasts are provided for every half hour "
                + "in the forecast period\n"
                + " Minutes in forecasted_start and forecasted_end "
                + f" should correspond to: {forecasted_minutes}"
            )
    # Check 3
    end_of_last_for_start = _determine_last_market_day_end_for_half_hourly(run_start)
    start_check_dt = end_of_last_for_start + timedelta(minutes=30)
    if forecasted_start < start_check_dt:
        print_allowed = start_check_dt.strftime(DATETIME_FORMAT)
        raise ValueError(
            f"For ST PASA, forecasted_start must be no earlier than {print_allowed} "
            + "based on the supplied run_start"
        )
    # Check 4
    end_of_last_for_end = _determine_last_market_day_end_for_half_hourly(run_end)
    end_check_dt = end_of_last_for_end + timedelta(days=6)
    if forecasted_end > end_check_dt:
        print_allowed = end_check_dt.strftime(DATETIME_FORMAT)
        raise ValueError(
            f"For ST PASA, forecasted_end must be no later than {print_allowed} "
            + "based on the supplied run_end"
        )
    return None


def validate_MTPASA_datetime_inputs(
    run_start: datetime,
    run_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """
    From `AEMO PASA Outputs <https://aemo.com.au/energy-systems/electricity/
    national-electricity-market-nem/data-nem/market-management-system-mms-data/
    projected-assessment-of-system-adequacy-pasa>`_:

      [MT PASA] is produced weekly (on Tuesdays) and lists the medium-term
      supply/demand prospects for the period two years in advance.
      The information is provided for each day within the report period.

    Noting that:

    - `MT PASA` is actually run at half-hourly resolution
      - But results are aggregated and reported for each day
    - Timing of "RUN_DATETIME" appears to be inconsistent on inspection
      - No validation on :attr:`run_start` and :attr:`run_end`
      - Compiler will instead collect all forecasts between provided forecast datetimes

    Validation checks:

    Check 1:
      `forecasted_start` and `forecasted_end` are at 00:00 for each supplied date.
      This is because results are reported for a day.
    Check 2:
      `forecasted_end` is within 2 years and 16 days of `run_end`. A 16 day offset
      appears to be in older data.Newer data appears to have a 6 day offset.

    Todo:
        Handle MTPASA DUID Availability

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
    Raises:
        ValueError: If any validation conditions are failed.
    """
    # Check 1
    for forecasted_input in (forecasted_start, forecasted_end):
        if forecasted_input.hour != 0 or forecasted_input.minute != 0:
            raise ValueError(
                "Results for MT PASA reported for each day. Forecasted start/end should"
                + " be supplied with hh:mm of 00:00"
            )
    # Check 2
    if run_end.month == 2 and run_end.day == 29:
        plus_two_years = run_end.replace(year=run_end.year + 2, day=28)
    else:
        plus_two_years = run_end.replace(year=run_end.year + 2)
    check_end_date = plus_two_years + timedelta(days=16)
    if forecasted_end > check_end_date:
        print_allowed = check_end_date.strftime(DATETIME_FORMAT)
        raise ValueError(
            f"For MT PASA, forecasted_end must be no later than {print_allowed} "
            + "based on the supplied run_end"
        )
    return None
