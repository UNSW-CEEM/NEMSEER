from datetime import datetime

from nemseer.loader import Loader, _dt_converter, _tablestr_converter


def test_minimal_dateinput():
    min_dt = _dt_converter("1/2/2021 2:3")
    assert min_dt == datetime(2021, 2, 1, 2, 3)


def test_tablestr_converter():
    assert _tablestr_converter("sdfs") == ["sdfs"]


class TestLoader:
    same_dates = ("01/02/2021 02:03", "01/02/2021 02:03")
    consecutive_dates = ("05/12/2021 23:03", "05/12/2021 23:04")
    backward_dates = ("03/06/2022 12:00", "06/03/2022 12:00")

    def test_same_dates(self):
        obj = Loader.initialise(
            self.same_dates[0],
            self.same_dates[1],
            self.consecutive_dates[0],
            self.consecutive_dates[1],
            "PREDISPATCH",
            "CONSTRAINT_D",
        )
        assert type(obj) is Loader
