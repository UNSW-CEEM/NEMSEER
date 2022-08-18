from datetime import datetime

import pytest

from nemseer.query import Query, _dt_converter, _enumerate_tables, _tablestr_converter


def test_minimal_dateinput():
    min_dt = _dt_converter("2021/2/1 2:3")
    assert min_dt == datetime(2021, 2, 1, 2, 3)


def test_tablestr_converter():
    assert _tablestr_converter("sdfs") == ["sdfs"]


def test_tablstr_redundant_conversion():
    assert _tablestr_converter(["sdfs"]) == ["sdfs"]


def test_enumerate_tables():
    tables = ["REGIONDISPATCH", "DISPATCHLOAD", "testing"]
    table_str = "testing"
    assert _enumerate_tables(tables, table_str, 2) == [
        "REGIONDISPATCH",
        "DISPATCHLOAD",
        "testing1",
        "testing2",
    ]


class TestQuery:
    same_forecast_dates = ("2021/02/01 02:03", "2021/02/01 02:03")
    consecutive_dates = ("2021/12/05 23:03", "2021/12/05 23:04")
    same_forecasted_dates = ("2021/12/06 02:03", "2021/12/06 02:03")

    backward_dates = ("2022/06/03 12:00", "2022/03/06 12:00")
    backward_dates_pair = ("2022/06/04 12:00", "2022/03/07 12:00")

    def test_same_forecast_dates(self, tmp_path):
        obj = Query.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
            tmp_path,
        )
        assert type(obj) is Query

    def test_same_forecasted_dates(self, tmp_path):
        obj = Query.initialise(
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            self.same_forecasted_dates[0],
            self.same_forecasted_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
            tmp_path,
        )
        assert type(obj) is Query

    def test_all_same_dates(self, tmp_path):
        with pytest.raises(ValueError):
            Query.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                tmp_path,
            )

    def test_incorrect_forecast_chronology(self, tmp_path):
        with pytest.raises(ValueError):
            Query.initialise(
                self.backward_dates[0],
                self.backward_dates[1],
                self.backward_dates_pair[0],
                self.backward_dates_pair[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                tmp_path,
            )

    def test_incorrect_forecasted_chronology(self, tmp_path):
        with pytest.raises(ValueError):
            Query.initialise(
                self.same_forecast_dates[0],
                self.same_forecast_dates[1],
                self.backward_dates[0],
                self.backward_dates[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                tmp_path,
            )

    def test_incorrect_relative_chronology(self, tmp_path):
        with pytest.raises(ValueError):
            Query.initialise(
                self.backward_dates[0],
                self.backward_dates_pair[0],
                self.backward_dates[1],
                self.backward_dates_pair[1],
                "PREDISPATCH",
                "CONSTRAINT_D",
                tmp_path,
            )

    def test_enumerated_tables(self, tmp_path):
        obj = Query.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "P5MIN",
            "CONSTRAINTSOLUTION",
            tmp_path,
        )
        assert obj.tables == ["CONSTRAINTSOLUTION"]

    def test_dir_validation(self, tmp_path):
        raw = tmp_path / "raw"
        raw.mkdir()
        processed = tmp_path / "processed"
        processed.mkdir()
        obj = Query.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
            raw_cache=raw,
            processed_cache=processed,
        )
        assert type(obj) is Query

    def test_distinct_dir_error(self, tmp_path):
        testdir = tmp_path / "same"
        testdir.mkdir()
        with pytest.raises(ValueError):
            Query.initialise(
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
            Query.initialise(
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
    def test_mtpasa_duidavailability(self, tmp_path):
        Query.initialise(
            self.backward_dates[0],
            self.backward_dates_pair[0],
            self.backward_dates[1],
            self.backward_dates_pair[1],
            "MTPASA",
            "DUIDAVAILABILITY",
            tmp_path,
        )