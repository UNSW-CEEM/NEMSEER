from datetime import timedelta

import pytest

from nemseer import forecast_types, generate_runtimes
from nemseer.data import DATETIME_FORMAT


@pytest.mark.parametrize("forecast_type", forecast_types)
@pytest.mark.parametrize("gen_n_datetimes", [5], indirect=True)
@pytest.mark.parametrize("end_delta_hours", [0, 1, 2, 6, 24, 168, 24 * 365])
def test_runtime_generation(
    gen_n_datetimes, forecast_type, end_delta_hours, fix_forecasted_dt
):
    for forecasted_start in gen_n_datetimes:
        forecasted_start = fix_forecasted_dt(forecasted_start, forecast_type)
        if forecast_type == "MTPASA" and end_delta_hours < 24:
            forecasted_end = forecasted_start
        else:
            forecasted_end = forecasted_start + timedelta(hours=end_delta_hours)
        (str_start, str_end) = (
            forecasted_start.strftime(DATETIME_FORMAT),
            forecasted_end.strftime(DATETIME_FORMAT),
        )
        generate_runtimes(str_start, str_end, forecast_type)
