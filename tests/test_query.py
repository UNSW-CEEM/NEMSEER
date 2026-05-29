from datetime import datetime

import pytest

from nemseer.data import DATETIME_FORMAT
from nemseer.query import (
    Query,
    _dt_converter,
    _enumerate_files_for_month,
    _tablestr_converter,
    generate_sqlloader_filenames,
)


def test_minimal_dateinput():
    min_dt = _dt_converter("2021/2/1 2:3")
    assert min_dt == datetime(2021, 2, 1, 2, 3)


def test_correct_minimal_seconds_input():
    dt = _dt_converter("2021/2/1 2:3:0")
    assert dt == datetime(2021, 2, 1, 2, 3, 0)


def test_correct_full_seconds_input():
    dt = _dt_converter("2021/02/01 20:30:00")
    assert dt == datetime(2021, 2, 1, 20, 30, 0)


def test_incorrect_seconds_input():
    with pytest.raises(ValueError):
        _dt_converter("2021/02/01 02:03:30")


def test_tablestr_converter():
    assert _tablestr_converter("sdfs") == ["sdfs"]


def test_tablstr_redundant_conversion():
    assert _tablestr_converter(["sdfs"]) == ["sdfs"]


def test_enumerate_files_for_month():
    assert _enumerate_files_for_month(2024, 7, "PREDISPATCH", "LOAD") == {
        (2024, 7, "LOAD", 1): "PUBLIC_DVD_PREDISPATCHLOAD1_202407010000",
        (2024, 7, "LOAD", 2): "PUBLIC_DVD_PREDISPATCHLOAD2_202407010000",
    }
    assert _enumerate_files_for_month(2024, 8, "PREDISPATCH", "LOAD") == {
        (
            2024,
            8,
            "LOAD",
            None,
        ): "PUBLIC_ARCHIVE%2523PREDISPATCHLOAD%2523ALL%2523FILE01%2523202408010000",
    }
    assert _enumerate_files_for_month(2024, 1, "P5MIN", "CONSTRAINTSOLUTION") == {
        (
            2024,
            1,
            "CONSTRAINTSOLUTION",
            1,
        ): "PUBLIC_DVD_P5MIN_CONSTRAINTSOLUTION1_202401010000",
        (
            2024,
            1,
            "CONSTRAINTSOLUTION",
            2,
        ): "PUBLIC_DVD_P5MIN_CONSTRAINTSOLUTION2_202401010000",
        (
            2024,
            1,
            "CONSTRAINTSOLUTION",
            3,
        ): "PUBLIC_DVD_P5MIN_CONSTRAINTSOLUTION3_202401010000",
        (
            2024,
            1,
            "CONSTRAINTSOLUTION",
            4,
        ): "PUBLIC_DVD_P5MIN_CONSTRAINTSOLUTION4_202401010000",
    }
    assert _enumerate_files_for_month(2024, 8, "P5MIN", "CONSTRAINTSOLUTION") == {
        (
            2024,
            8,
            "CONSTRAINTSOLUTION",
            1,
        ): "PUBLIC_ARCHIVE%2523P5MIN_CONSTRAINTSOLUTION%2523FILE01%2523202408010000",
        (
            2024,
            8,
            "CONSTRAINTSOLUTION",
            2,
        ): "PUBLIC_ARCHIVE%2523P5MIN_CONSTRAINTSOLUTION%2523FILE02%2523202408010000",
        (
            2024,
            8,
            "CONSTRAINTSOLUTION",
            3,
        ): "PUBLIC_ARCHIVE%2523P5MIN_CONSTRAINTSOLUTION%2523FILE03%2523202408010000",
    }
    assert _enumerate_files_for_month(2024, 1, "STPASA", "REGIONSOLUTION") == {
        (
            2024,
            1,
            "REGIONSOLUTION",
            None,
        ): "PUBLIC_DVD_STPASA_REGIONSOLUTION_202401010000"
    }
    assert _enumerate_files_for_month(2024, 8, "STPASA", "REGIONSOLUTION") == {
        (
            2024,
            8,
            "REGIONSOLUTION",
            None,
        ): "PUBLIC_ARCHIVE%2523STPASA_REGIONSOLUTION%2523FILE01%2523202408010000"
    }


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
        obj = Query.initialise(
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            self.same_forecast_dates[0],
            self.same_forecast_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
            tmp_path,
        )
        assert type(obj) is Query

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

    def test_p5constraintsolution_filename_generation(self):
        fnames = generate_sqlloader_filenames(
            datetime.strptime(self.same_forecast_dates[0], DATETIME_FORMAT),
            datetime.strptime(self.same_forecast_dates[1], DATETIME_FORMAT),
            "P5MIN",
            ["CONSTRAINTSOLUTION"],
        ).values()
        test_fnames = [
            f"PUBLIC_DVD_P5MIN_CONSTRAINTSOLUTION{i}_202102010000" for i in range(1, 5)
        ]
        assert set(fnames) == set(test_fnames)
        fnames = generate_sqlloader_filenames(
            datetime(2024, 8, 4, 15, 0),
            datetime(2024, 8, 4, 15, 0),
            "P5MIN",
            ["CONSTRAINTSOLUTION"],
        ).values()
        test_fnames = [
            f"PUBLIC_ARCHIVE%2523P5MIN_CONSTRAINTSOLUTION%2523FILE0{i}%2523202408010000"
            for i in range(1, 4)
        ]
        assert set(fnames) == set(test_fnames)

    def test_edge_case_dates_with_filename_generation(self):
        forecast_type = "STPASA"
        table = ["REGIONSOLUTION"]
        (r_start_1, r_end_1) = (
            datetime.strptime("2021/01/31 23:00", DATETIME_FORMAT),
            datetime.strptime("2021/02/01 00:00", DATETIME_FORMAT),
        )
        test_1 = generate_sqlloader_filenames(r_start_1, r_end_1, forecast_type, table)
        assert len(test_1.values()) == 1
        (r_start_2, r_end_2) = (
            datetime.strptime("2021/01/31 23:00", DATETIME_FORMAT),
            datetime.strptime("2021/02/01 01:00", DATETIME_FORMAT),
        )
        test_2 = generate_sqlloader_filenames(r_start_2, r_end_2, forecast_type, table)
        assert len(test_2.values()) == 2
        (r_start_3, r_end_3) = (
            datetime.strptime("2021/12/31 23:55", DATETIME_FORMAT),
            datetime.strptime("2022/01/06 01:00", DATETIME_FORMAT),
        )
        test_3 = generate_sqlloader_filenames(r_start_3, r_end_3, forecast_type, table)
        assert len(test_3.values()) == 2

        (r_start_4, r_end_4) = (
            datetime.strptime("2021/12/31 23:55", DATETIME_FORMAT),
            datetime.strptime("2023/01/06 01:00", DATETIME_FORMAT),
        )
        test_4 = generate_sqlloader_filenames(r_start_4, r_end_4, forecast_type, table)
        assert len(test_4.values()) == 14

    def test_check_raw_cache(self, download_file_to_cache):
        assert download_file_to_cache.check_all_raw_data_in_cache()
