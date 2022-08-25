from datetime import datetime, timedelta

import pytest

from nemseer.forecast_type.validators import (
    _determine_last_market_day_end_for_half_hourly,
    validate_MTPASA_datetime_inputs,
    validate_P5MIN_datetime_inputs,
    validate_PDPASA_datetime_inputs,
    validate_PREDISPATCH_datetime_inputs,
    validate_STPASA_datetime_inputs,
)


class TestP5MINvalidator:
    @pytest.mark.parametrize("minutes", range(0, 60, 5))
    def test_valid_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=minutes)
        run_end = run_start + timedelta(minutes=5)
        forecasted_start = run_end
        forecasted_end = run_end + timedelta(minutes=5)
        assert (
            validate_P5MIN_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )

    @pytest.mark.parametrize("minutes", [4, 13, 22, 39, 54])
    def test_invalid_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=minutes)
        run_end = run_start + timedelta(minutes=5)
        forecasted_start = run_end
        forecasted_end = run_end + timedelta(minutes=5)
        with pytest.raises(ValueError):
            validate_P5MIN_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_too_late(self, gen_datetime):
        run_start = gen_datetime.replace(minute=25)
        run_end = run_start + timedelta(minutes=5)
        forecasted_start = run_end
        forecasted_end = run_end + timedelta(minutes=60)
        with pytest.raises(ValueError):
            validate_P5MIN_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )


class TestPREDISPATCH_and_PASA_validators:
    @pytest.mark.parametrize("minutes", (0, 30))
    def test_valid_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=minutes)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_end
        forecasted_end = run_end + timedelta(minutes=60)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )
        assert (
            validate_PDPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )

    @pytest.mark.parametrize("minutes", [5, 13, 22, 39, 54])
    def test_invalid_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=minutes)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_end
        forecasted_end = run_end + timedelta(minutes=60)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_ok(self):
        run_start_1 = datetime(2021, 2, 1, 11, 30)
        run_end_1 = run_start_1 + timedelta(minutes=60)
        forecasted_start_1 = run_end_1
        forecasted_end_1 = datetime(2021, 2, 2, 4, 0)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                run_start_1, run_end_1, forecasted_start_1, forecasted_end_1
            )
        ) is None
        assert (
            validate_PDPASA_datetime_inputs(
                run_start_1, run_end_1, forecasted_start_1, forecasted_end_1
            )
        ) is None
        run_start_2 = datetime(2021, 2, 1, 12, 00)
        run_end_2 = run_start_2 + timedelta(minutes=60)
        forecasted_start_2 = run_end_2
        forecasted_end_2 = datetime(2021, 2, 3, 4, 0)
        assert (
            validate_PREDISPATCH_datetime_inputs(
                run_start_2, run_end_2, forecasted_start_2, forecasted_end_2
            )
        ) is None
        assert (
            validate_PDPASA_datetime_inputs(
                run_start_2, run_end_2, forecasted_start_2, forecasted_end_2
            )
        ) is None

    def test_forecasted_end_too_late(self):
        run_start_1 = datetime(2021, 2, 1, 11, 30)
        run_end_1 = run_start_1 + timedelta(minutes=60)
        forecasted_start_1 = run_end_1
        forecasted_end_1 = datetime(2021, 2, 2, 4, 30)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                run_start_1, run_end_1, forecasted_start_1, forecasted_end_1
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                run_start_1, run_end_1, forecasted_start_1, forecasted_end_1
            )
        run_start_2 = datetime(2021, 2, 1, 12, 00)
        run_end_2 = run_start_2 + timedelta(minutes=60)
        forecasted_start_2 = run_end_2
        forecasted_end_2 = datetime(2021, 2, 3, 4, 30)
        with pytest.raises(ValueError):
            validate_PREDISPATCH_datetime_inputs(
                run_start_2, run_end_2, forecasted_start_2, forecasted_end_2
            )
        with pytest.raises(ValueError):
            validate_PDPASA_datetime_inputs(
                run_start_2, run_end_2, forecasted_start_2, forecasted_end_2
            )


class TestSTPASAvalidator:
    def test_valid_minutes(self, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_start + timedelta(days=3, minutes=30)
        forecasted_end = forecasted_start + timedelta(minutes=30)
        assert (
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )

    @pytest.mark.parametrize("minutes", [4, 15, 30, 39, 55])
    def test_invalid_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=minutes, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_start + timedelta(days=3, minutes=30)
        forecasted_end = forecasted_start + timedelta(minutes=30)
        with pytest.raises(ValueError):
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    @pytest.mark.parametrize("minutes", [4, 15, 31, 39, 55])
    def test_invalid_forecasted_minutes(self, minutes, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_start + timedelta(days=3, minutes=minutes)
        forecasted_end = forecasted_start + timedelta(minutes=30)
        with pytest.raises(ValueError):
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_start_too_early(self, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = _determine_last_market_day_end_for_half_hourly(run_start)
        forecasted_end = forecasted_start + timedelta(minutes=60)
        with pytest.raises(ValueError):
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_start_ok(self, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = _determine_last_market_day_end_for_half_hourly(
            run_start
        ) + timedelta(minutes=30)
        forecasted_end = forecasted_start + timedelta(minutes=60)
        assert (
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )

    def test_forecasted_end_too_late(self, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_start + timedelta(days=3)
        forecasted_end = _determine_last_market_day_end_for_half_hourly(
            run_end
        ) + timedelta(days=6, minutes=30)
        with pytest.raises(ValueError):
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_of(self, gen_datetime):
        run_start = gen_datetime.replace(minute=0, second=0, microsecond=0)
        run_end = run_start + timedelta(minutes=60)
        forecasted_start = run_start + timedelta(days=3)
        forecasted_end = _determine_last_market_day_end_for_half_hourly(
            run_end
        ) + timedelta(days=6)
        assert (
            validate_STPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
            is None
        )


class TestMTPASAvalidator:
    def test_invalid_minutes(self):
        run_start = datetime(2020, 2, 1)
        run_end = datetime(2020, 2, 28)
        forecasted_start = datetime(2021, 5, 1, minute=38)
        forecasted_end = datetime(2022, 3, 16)
        with pytest.raises(ValueError):
            validate_MTPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_ok(self):
        run_start = datetime(2020, 2, 1)
        run_end = datetime(2020, 2, 28)
        forecasted_start = datetime(2021, 5, 1)
        forecasted_end = datetime(2022, 3, 16)
        assert (
            validate_MTPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
        ) is None

    def test_forecasted_end_too_late_29_feb(self):
        run_start = datetime(2020, 2, 1)
        run_end = datetime(2020, 2, 29)
        forecasted_start = datetime(2021, 5, 1)
        forecasted_end = datetime(2022, 3, 17)
        with pytest.raises(ValueError):
            validate_MTPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )

    def test_forecasted_end_too_late(self):
        run_start = datetime(2020, 2, 1)
        run_end = datetime(2020, 2, 28)
        forecasted_start = datetime(2021, 5, 1)
        forecasted_end = datetime(2022, 3, 17)
        with pytest.raises(ValueError):
            validate_MTPASA_datetime_inputs(
                run_start, run_end, forecasted_start, forecasted_end
            )
