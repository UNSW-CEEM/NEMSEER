from datetime import datetime, timedelta


def validate_P5MIN_datetime_inputs(
    forecast_start: datetime,
    forecast_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
) -> None:
    """Validates `P5MIN` forecast datetime inputs

    From AEMO MMS Data Model Report:

    > The 5-minute Predispatch cycle runs every 5-minutes to produce a dispatch and
    > pricing schedule to a 5-minute resolution covering the next hour,
    > a total of twelve periods.

    Validation checks:

    1. Minute component of datetime inputs is on a 5 minute basis
    2. `forecasted_end` is not more than 55 minutes (12 cycles) from `forecast_end`

    These 12 dispatch cycles include the immediate interval
    (i.e. where `RUN_DATETIME` = `INTERVAL_DATETIME`)
    """
    acceptable_minutes = set(range(0, 60, 5))
    for dt_input in (forecast_start, forecast_end, forecasted_start, forecasted_end):
        if dt_input.minute not in acceptable_minutes:
            raise ValueError(
                "P5MIN is run every 5 minutes."
                + " Minutes in datetime inputs should correspond to:\n"
                + f"{acceptable_minutes}"
            )
    if forecasted_end > forecast_end + timedelta(minutes=55):
        raise ValueError(
            "For P5MIN, forecasted_end must be within 55 minutes of forecast_end"
        )


def validate_PREDISPATCH_inputs():
    """
    .. todo:: Create `PREDISPATCH` validator
    """
    return None


def validate_PDPASA_inputs():
    """
    .. todo:: Create `PDPASA` validator
    """
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
