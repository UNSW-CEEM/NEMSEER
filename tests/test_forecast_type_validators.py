from datetime import timedelta

import pytest

from nemseer.forecast_type_validators import validate_P5MIN_datetime_inputs


class TestP5MINvalidator:
    @pytest.mark.parametrize("minutes", range(0, 60, 5))
    def test_valid_minutes(self, minutes, gen_datetime):
        forecast_start = gen_datetime.replace(minute=minutes)
        forecast_end = forecast_start + timedelta(minutes=5)
        forecasted_start = forecast_end
        forecasted_end = forecast_end + timedelta(minutes=5)
        assert (
            validate_P5MIN_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )
            is None
        )

    @pytest.mark.parametrize("minutes", [4, 13, 22, 39, 54])
    def test_invalid_minutes(self, minutes, gen_datetime):
        forecast_start = gen_datetime.replace(minute=minutes)
        forecast_end = forecast_start + timedelta(minutes=5)
        forecasted_start = forecast_end
        forecasted_end = forecast_end + timedelta(minutes=5)
        with pytest.raises(ValueError):
            validate_P5MIN_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_too_late(self, gen_datetime):
        forecast_start = gen_datetime.replace(minute=25)
        forecast_end = forecast_start + timedelta(minutes=5)
        forecasted_start = forecast_end
        forecasted_end = forecast_end + timedelta(minutes=56)
        with pytest.raises(ValueError):
            validate_P5MIN_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )
