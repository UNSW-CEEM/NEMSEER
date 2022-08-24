from datetime import datetime, timedelta

import pytest

from nemseer.forecast_type.validators import (
    validate_P5MIN_datetime_inputs,
    validate_PDPASA_datetime_inputs,
    validate_PREDISPATCH_datetime_inputs,
)


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


class TestPREDISPATCH_and_PASA_validators:
    @pytest.mark.parametrize("minutes", (0, 30))
    def test_valid_minutes(self, minutes, gen_datetime):
        forecast_start = gen_datetime.replace(minute=minutes)
        forecast_end = forecast_start + timedelta(minutes=60)
        forecasted_start = forecast_end
        forecasted_end = forecast_end + timedelta(minutes=60)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )
            is None
        )
        assert (
            validate_PDPASA_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )
            is None
        )

    @pytest.mark.parametrize("minutes", [5, 13, 22, 39, 54])
    def test_invalid_minutes(self, minutes, gen_datetime):
        forecast_start = gen_datetime.replace(minute=minutes)
        forecast_end = forecast_start + timedelta(minutes=60)
        forecasted_start = forecast_end
        forecasted_end = forecast_end + timedelta(minutes=60)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                forecast_start, forecast_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_ok(self):
        forecast_start_1 = datetime(2021, 2, 1, 11, 30)
        forecast_end_1 = forecast_start_1 + timedelta(minutes=60)
        forecasted_start_1 = forecast_end_1
        forecasted_end_1 = datetime(2021, 2, 2, 4, 0)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                forecast_start_1, forecast_end_1, forecasted_start_1, forecasted_end_1
            )
        ) is None
        assert (
            validate_PDPASA_datetime_inputs(
                forecast_start_1, forecast_end_1, forecasted_start_1, forecasted_end_1
            )
        ) is None
        forecast_start_2 = datetime(2021, 2, 1, 12, 00)
        forecast_end_2 = forecast_start_2 + timedelta(minutes=60)
        forecasted_start_2 = forecast_end_2
        forecasted_end_2 = datetime(2021, 2, 3, 4, 0)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                forecast_start_2, forecast_end_2, forecasted_start_2, forecasted_end_2
            )
        ) is None
        assert (
            validate_PDPASA_datetime_inputs(
                forecast_start_2, forecast_end_2, forecasted_start_2, forecasted_end_2
            )
        ) is None

    def test_forecasted_end_too_late(self):
        forecast_start_1 = datetime(2021, 2, 1, 11, 30)
        forecast_end_1 = forecast_start_1 + timedelta(minutes=60)
        forecasted_start_1 = forecast_end_1
        forecasted_end_1 = datetime(2021, 2, 2, 4, 30)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                forecast_start_1, forecast_end_1, forecasted_start_1, forecasted_end_1
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                forecast_start_1, forecast_end_1, forecasted_start_1, forecasted_end_1
            )
        forecast_start_2 = datetime(2021, 2, 1, 12, 00)
        forecast_end_2 = forecast_start_2 + timedelta(minutes=60)
        forecasted_start_2 = forecast_end_2
        forecasted_end_2 = datetime(2021, 2, 3, 4, 30)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                forecast_start_2, forecast_end_2, forecasted_start_2, forecasted_end_2
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                forecast_start_2, forecast_end_2, forecasted_start_2, forecasted_end_2
            )
