from datetime import datetime

import pytest

from nemseer.loader import Loader, _dt_converter, _tablestr_converter


def test_minimal_dateinput():
    min_dt = _dt_converter("1/2/2021 2:3")
    assert min_dt == datetime(2021, 2, 1, 2, 3)


def test_tablestr_converter():
    assert _tablestr_converter("sdfs") == ["sdfs"]


def test_tablstr_redundant_conversion():
    assert _tablestr_converter(["sdfs"]) == ["sdfs"]


class TestLoader:
    same_forecast_dates = ("01/02/2021 02:03", "01/02/2021 02:03")
    consecutive_dates = ("05/12/2021 23:03", "05/12/2021 23:04")
    same_forecasted_dates = ("06/12/2021 02:03", "06/12/2021 02:03")

    backward_dates = ("03/06/2022 12:00", "06/03/2022 12:00")
    backward_dates_pair = ("04/06/2022 12:00", "07/03/2022 12:00")

    def test_same_forecast_dates(self):
        obj = Loader.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
        )
        assert type(obj) is Loader

    def test_same_forecasted_dates(self):
        obj = Loader.initialise(
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            self.same_forecasted_dates[0],
            self.same_forecasted_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
        )
        assert type(obj) is Loader

    def test_all_same_dates(self):
        with pytest.raises(ValueError):
            Loader.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
            )

    def test_incorrect_forecast_chronology(self):
        with pytest.raises(ValueError):
            Loader.initialise(
                self.backward_dates[0],
                self.backward_dates[1],
                self.backward_dates_pair[0],
                self.backward_dates_pair[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
            )

    def test_incorrect_forecasted_chronology(self):
        with pytest.raises(ValueError):
            Loader.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.backward_dates[0],
                self.backward_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
            )

    def test_incorrect_relative_chronology(self):
        with pytest.raises(ValueError):
            Loader.initialise(
                self.backward_dates[0],
                self.backward_dates_pair[0],
                self.backward_dates[1],
                self.backward_dates_pair[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
            )

    def test_enumerated_tables(self):
        obj = Loader.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "P5MIN",
            "CONSTRAINTSOLUTION",
        )
        assert obj.tables == ["CONSTRAINTSOLUTION"]

    def test_dir_validation(self, tmp_path):
        raw = tmp_path / "raw"
        raw.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()
        obj = Loader.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
            raw_cache=raw,
            processed_cache=processed,
        )
        assert type(obj) is Loader

    def test_distinct_dir_error(self, tmp_path):
        testdir = tmp_path / "same"
        testdir.mkdir()
        with pytest.raises(ValueError):
            Loader.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.consecutive_dates[0],
                self.consecutive_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                raw_cache=testdir,
                processed_cache=testdir,
            )

    def test_dir_creation(self, tmp_path):
        testdir = tmp_path / "yettobe"
        with pytest.raises(ValueError):
            Loader.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.consecutive_dates[0],
                self.consecutive_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                raw_cache=testdir,
                processed_cache=testdir,
            )

    @pytest.mark.xfail(raises=ValueError)
    def test_mtpasa_duidavailability(self):
        Loader.initialise(
            self.backward_dates[0],
            self.backward_dates_pair[0],
            self.backward_dates[1],
            self.backward_dates_pair[1],
            "MTPASA",
            "DUIDAVAILABILITY",
        )
