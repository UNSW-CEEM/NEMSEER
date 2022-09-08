import random
from datetime import datetime, timedelta

import pytest

from nemseer import forecast_types, generate_runtimes, get_tables
from nemseer.data import DATETIME_FORMAT
from nemseer.data_compilers import DataCompiler, _map_files_to_table
from nemseer.query import Query


def test_map_files_to_table():
    run_start, run_end = generate_runtimes(
        "2020/02/01 00:00", "2020/02/02 00:00", "PREDISPATCH"
    )
    run_start = datetime.strptime(run_start, DATETIME_FORMAT)
    run_end = datetime.strptime(run_end, DATETIME_FORMAT)
    assert _map_files_to_table(
        run_start, run_end, "PREDISPATCH", ["PRICE", "PRICE_D"]
    ) == {
        "PRICE": ["PUBLIC_DVD_PREDISPATCHPRICE_202001010000"],
        "PRICE_D": ["PUBLIC_DVD_PREDISPATCHPRICE_D_202001010000"],
    }


def test_map_enumerated_files_to_table():
    run_start, run_end = generate_runtimes(
        "2020/02/01 00:00", "2020/02/02 00:00", "PREDISPATCH"
    )
    run_start = datetime.strptime(run_start, DATETIME_FORMAT)
    run_end = datetime.strptime(run_end, DATETIME_FORMAT)
    assert _map_files_to_table(run_start, run_end, "PREDISPATCH", ["LOAD"]) == {
        "LOAD": [
            "PUBLIC_DVD_PREDISPATCHLOAD1_202001010000",
            "PUBLIC_DVD_PREDISPATCHLOAD2_202001010000",
        ],
    }


def create_test_tables():
    p5min_tabs = get_tables(2020, 1, "P5MIN")
    pd_tabs = get_tables(2020, 1, "PREDISPATCH")
    pdpasa_tabs = get_tables(2020, 1, "PDPASA")
    stpasa_tabs = get_tables(2020, 1, "STPASA")
    mtpasa_tabs = get_tables(2020, 1, "MTPASA")
    test_tables = {}
    for tabs, ftype in zip(
        (p5min_tabs, pd_tabs, pdpasa_tabs, stpasa_tabs, mtpasa_tabs), forecast_types
    ):
        ind = random.randrange(0, len(tabs))
        test_tables[ftype] = tabs[ind]
    return test_tables


def test_invalid_forecasted_times_for_runtime_generation():
    with pytest.raises(ValueError):
        generate_runtimes("2021/01/01 00:00", "2020/01/01 00:00", "STPASA")


class TestDataCompiler:
    tables = create_test_tables()

    @pytest.mark.parametrize("forecast_type", forecast_types)
    @pytest.mark.parametrize("gen_n_datetimes", [5], indirect=True)
    @pytest.mark.parametrize("end_delta_hours", [0, 1, 2, 6, 24, 168, 24 * 365])
    def test_runtime_generation_and_DataCompiler_initialisation(
        self,
        gen_n_datetimes,
        forecast_type,
        end_delta_hours,
        fix_forecasted_dt,
        tmp_path,
    ):
        for forecasted_start in gen_n_datetimes:
            forecasted_start = fix_forecasted_dt(forecasted_start, forecast_type)
            if forecast_type == "MTPASA" and end_delta_hours < 24:
                forecasted_end = forecasted_start
            else:
                forecasted_end = forecasted_start + timedelta(hours=end_delta_hours)
            forecasted_start = forecasted_start.strftime(DATETIME_FORMAT)
            forecasted_end = forecasted_end.strftime(DATETIME_FORMAT)
            (str_start, str_end) = (forecasted_start, forecasted_end)
            run_start, run_end = generate_runtimes(str_start, str_end, forecast_type)
            query = Query.initialise(
                run_start,
                run_end,
                forecasted_start,
                forecasted_end,
                forecast_type,
                self.tables[forecast_type],
                tmp_path,
            )
            datacomp = DataCompiler.from_Query(query)
            assert type(datacomp) is DataCompiler
