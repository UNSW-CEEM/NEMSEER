import logging
from datetime import datetime, timedelta

import pandas as pd
import pytest

from nemseer import compile_raw_data, download_raw_data
from nemseer.data import DATETIME_FORMAT, FORECASTED_COL, RUNTIME_COL
from nemseer.forecast_type.run_time_generators import generate_runtimes


class TestDowloadRawData:
    def test_download_and_query_check(self, caplog, download_file_to_cache):
        query = download_file_to_cache
        caplog.set_level(logging.INFO)
        download_raw_data(
            query.run_start.strftime(DATETIME_FORMAT),
            query.run_end.strftime(DATETIME_FORMAT),
            query.forecasted_start.strftime(DATETIME_FORMAT),
            query.forecasted_end.strftime(DATETIME_FORMAT),
            query.forecast_type,
            query.tables,
            query.raw_cache,
        )
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "Query raw data already downloaded to" in record.msg
            ]
        )


class TestCompileRawData:
    def setup_compilation_test(
        self, gen_datetime, fix_forecasted_dt, forecast_type, time_delta
    ):
        forecasted_start = gen_datetime
        forecasted_start = fix_forecasted_dt(forecasted_start, forecast_type)
        forecasted_end = forecasted_start + time_delta
        forecasted_start = forecasted_start.strftime(DATETIME_FORMAT)
        forecasted_end = forecasted_end.strftime(DATETIME_FORMAT)

        (str_start, str_end) = (forecasted_start, forecasted_end)
        run_start, run_end = generate_runtimes(str_start, str_end, forecast_type)
        return run_start, run_end, forecasted_start, forecasted_end

    def test_invalid_format(
        self,
        gen_datetime,
        fix_forecasted_dt,
        tmp_path,
    ):
        (forecast_type, table) = ("STPASA", "INTERCONNECTORSOLN")
        time_delta = timedelta(hours=12, minutes=30)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        with pytest.raises(ValueError):
            compile_raw_data(
                run_start,
                run_end,
                forecasted_start,
                forecasted_end,
                forecast_type,
                table,
                raw_cache=tmp_path,
                data_format="csv",
            )

    def test_compile_two_datetime_cols(
        self,
        gen_datetime,
        fix_forecasted_dt,
        tmp_path,
    ):
        (forecast_type, table) = ("STPASA", "INTERCONNECTORSOLN")
        time_delta = timedelta(hours=12, minutes=30)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        data_map = compile_raw_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=tmp_path,
            data_format="df",
        )
        runtime_col = RUNTIME_COL[forecast_type]
        forecasted_col = FORECASTED_COL[forecast_type]
        assert data_map is not None
        df = data_map[table]
        run_start = datetime.strptime(run_start, DATETIME_FORMAT)
        run_end = datetime.strptime(run_end, DATETIME_FORMAT)
        forecasted_start = datetime.strptime(forecasted_start, DATETIME_FORMAT)
        forecasted_end = datetime.strptime(forecasted_end, DATETIME_FORMAT)
        assert pd.Timestamp(df[runtime_col].unique()[0]) >= run_start
        assert pd.Timestamp(df[runtime_col].unique()[-1]) <= run_end
        assert pd.Timestamp(df[forecasted_col].unique()[0]) >= forecasted_start
        assert pd.Timestamp(df[forecasted_col].unique()[-1]) <= forecasted_end

    def test_compile_one_datetime_col(
        self,
        gen_datetime,
        fix_forecasted_dt,
        tmp_path,
    ):
        (forecast_type, table) = ("PREDISPATCH", "CASESOLUTION")
        time_delta = timedelta(hours=2, minutes=30)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        data_map = compile_raw_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=tmp_path,
            data_format="df",
        )
        runtime_col = RUNTIME_COL[forecast_type]
        assert data_map is not None
        df = data_map[table]
        run_start = datetime.strptime(run_start, DATETIME_FORMAT)
        run_end = datetime.strptime(run_end, DATETIME_FORMAT)
        assert pd.Timestamp(df[runtime_col].unique()[0]) >= run_start
        assert pd.Timestamp(df[runtime_col].unique()[-1]) <= run_end
