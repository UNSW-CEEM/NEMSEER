from datetime import timedelta

import pytest

from nemseer import forecast_types, generate_runtimes
from nemseer.data import DATETIME_FORMAT


@pytest.mark.parametrize("forecast_type", forecast_types)
@pytest.mark.parametrize("gen_n_datetimes", [5], indirect=True)
@pytest.mark.parametrize("end_delta_hours", [0, 1, 2, 6, 24, 168, 24 * 365])
def test_runtime_generation(gen_n_datetimes, forecast_type, end_delta_hours):
    for forecasted_start in gen_n_datetimes:
        forecasted_start = forecasted_start.replace(second=0, microsecond=0)
        if forecast_type == "P5MIN":
            forecasted_start = forecasted_start.replace(minute=25)
        elif forecast_type in ["PDPASA", "PREDISPATCH"]:
            forecasted_start = forecasted_start.replace(minute=30)
        elif forecast_type == "MTPASA":
            forecasted_start = forecasted_start.replace(hour=0, minute=0)
        else:
            forecasted_start = forecasted_start.replace(minute=0)
        if forecast_type == "MTPASA" and end_delta_hours < 24:
            forecasted_end = forecasted_start
        else:
            forecasted_end = forecasted_start + timedelta(hours=end_delta_hours)
        (str_start, str_end) = (
            forecasted_start.strftime(DATETIME_FORMAT),
            forecasted_end.strftime(DATETIME_FORMAT),
        )
        generate_runtimes(str_start, str_end, forecast_type)
