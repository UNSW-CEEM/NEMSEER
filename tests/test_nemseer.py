import logging
from datetime import datetime, timedelta

import pandas as pd
import pytest
import xarray as xr

from nemseer import compile_data, download_raw_data
from nemseer.data import (
    DATETIME_FORMAT,
    FORECASTED_COL,
    INVALID_STUBS_FILE,
    RUNTIME_COL,
)
from nemseer.data_handlers import to_xarray
from nemseer.forecast_type.run_time_generators import generate_runtimes
from nemseer.query import generate_sqlloader_filenames


class TestDowloadRawData:
    def test_download_and_query_check(self, caplog, download_file_to_cache):
        query = download_file_to_cache
        caplog.set_level(logging.INFO)
        download_raw_data(
            query.forecast_type,
            query.tables,
            query.raw_cache,
            run_start=query.run_start.strftime(DATETIME_FORMAT),
            run_end=query.run_end.strftime(DATETIME_FORMAT),
        )
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "Query raw data already downloaded to" in record.msg
            ]
        )

    def test_mixed_datetimes_fail(self, tmp_path):
        run_start = "2020/01/01 00:00"
        forecasted_end = "2020/01/01 00:00"
        with pytest.raises(ValueError):
            download_raw_data(
                "STPASA",
                "REGIONSOLUTION",
                tmp_path,
                run_start=run_start,
                forecasted_end=forecasted_end,
            )

    def test_extra_datetime_fails(self, tmp_path):
        run_start = "2020/01/01 00:00"
        run_end = "2020/01/01 00:00"
        forecasted_end = "2020/01/01 00:00"
        with pytest.raises(ValueError):
            download_raw_data(
                "STPASA",
                "REGIONSOLUTION",
                tmp_path,
                run_start=run_start,
                run_end=run_end,
                forecasted_end=forecasted_end,
            )

    def test_runtime_generation(self, tmp_path, gen_datetime, mocker):
        def mock_download(query, keep_csv):
            return None

        forecasted_start = gen_datetime.replace(minute=30).strftime(DATETIME_FORMAT)
        forecasted_end = forecasted_start
        mocker.patch("nemseer.nemseer._initiate_downloads_from_query", mock_download)
        download_raw_data(
            "STPASA",
            "REGIONSOLUTION",
            tmp_path,
            forecasted_start=forecasted_start,
            forecasted_end=forecasted_end,
        )

    def test_forecasted_generation(self, tmp_path, gen_datetime, mocker):
        def mock_download(query, keep_csv):
            return None

        run_start = gen_datetime.replace(minute=30).strftime(DATETIME_FORMAT)
        run_end = run_start
        mocker.patch("nemseer.nemseer._initiate_downloads_from_query", mock_download)
        download_raw_data(
            "STPASA", "REGIONSOLUTION", tmp_path, run_start=run_start, run_end=run_end
        )


class TestCompileData:
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

    def test_all_query_files_invalid(
        self,
        gen_datetime,
        fix_forecasted_dt,
        tmp_path,
    ):
        (forecast_type, table) = ("STPASA", "REGIONSOLUTION")
        time_delta = timedelta(hours=72)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        fnames = generate_sqlloader_filenames(
            datetime.strptime(run_start, DATETIME_FORMAT),
            datetime.strptime(run_end, DATETIME_FORMAT),
            forecast_type,
            [table],
        ).values()
        stubfile = tmp_path / INVALID_STUBS_FILE
        with open(stubfile, "x") as f:
            for fn in fnames:
                f.write(f"{fn}\n")
        with pytest.raises(ValueError):
            compile_data(
                run_start,
                run_end,
                forecasted_start,
                forecasted_end,
                forecast_type,
                table,
                tmp_path,
            )

    def test_invalid_files_in_query(
        self,
        gen_datetime,
        fix_forecasted_dt,
        mocker,
        tmp_path,
        caplog,
    ):
        def mock_pd_concat(dfs, axis=0):
            return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        (forecast_type, table) = ("MTPASA", "RESERVELIMIT")
        time_delta = timedelta(hours=0)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        fnames = list(
            generate_sqlloader_filenames(
                datetime.strptime(run_start, DATETIME_FORMAT),
                datetime.strptime(run_end, DATETIME_FORMAT),
                forecast_type,
                [table],
            ).values()
        )
        stubfile = tmp_path / INVALID_STUBS_FILE
        with open(stubfile, "x") as f:
            for fn in fnames[:-1]:
                f.write(f"{fn}\n")
        caplog.set_level(logging.WARNING)
        mocker.patch("nemseer.data_compilers.pd.concat", mock_pd_concat)
        compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            tmp_path,
        )
        assert all(
            [INVALID_STUBS_FILE in record.msg for record in caplog.get_records("call")]
        )

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
            compile_data(
                run_start,
                run_end,
                forecasted_start,
                forecasted_end,
                forecast_type,
                table,
                raw_cache=tmp_path,
                data_format="csv",
            )

    def test_duplicated_rows_warning(
        self, gen_datetime, fix_forecasted_dt, tmp_path, caplog
    ):
        (forecast_type, table) = ("MTPASA", "RESERVELIMIT")
        time_delta = timedelta(days=1)
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = self.setup_compilation_test(
            gen_datetime, fix_forecasted_dt, forecast_type, time_delta
        )
        caplog.set_level(logging.WARNING)
        compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=tmp_path,
            data_format="df",
        )
        assert any(
            [
                (
                    "Duplicate rows detected whilst concatenating data. "
                    + "Dropping these rows."
                )
                in record.msg
                for record in caplog.get_records("call")
            ]
        )

    def test_write_to_processed_cache(self, compile_data_to_processed_cache):
        query_metadata = compile_data_to_processed_cache
        for forecast_type in query_metadata:
            processed_cache = query_metadata[forecast_type]["processed_cache"]
            table = query_metadata[forecast_type]["tables"]
            parq = processed_cache.glob("*.parquet")
            nc = processed_cache.glob("*.nc")
            assert (
                len(
                    [fn for fn in parq if forecast_type in fn.name and table in fn.name]
                )
                == 1
            )
            assert (
                len([fn for fn in nc if forecast_type in fn.name and table in fn.name])
                == 1
            )

    def test_compile_two_datetime_cols(
        self,
        compile_data_to_processed_cache,
    ):
        query_metadata = compile_data_to_processed_cache["STPASA"]
        (run_start, run_end) = (query_metadata["run_start"], query_metadata["run_end"])
        (forecasted_start, forecasted_end) = (
            query_metadata["forecasted_start"],
            query_metadata["forecasted_end"],
        )
        (forecast_type, table) = (
            query_metadata["forecast_type"],
            query_metadata["tables"],
        )
        raw_cache = query_metadata["raw_cache"]
        data_map = compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=raw_cache,
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

    def test_compile_one_datetime_col(self, compile_data_to_processed_cache):
        forecast_type = "P5MIN"
        query_metadata = compile_data_to_processed_cache[forecast_type]
        (run_start, run_end) = (query_metadata["run_start"], query_metadata["run_end"])
        table = query_metadata["tables"]
        data_map = compile_data(
            **query_metadata,
            data_format="df",
        )
        runtime_col = RUNTIME_COL[forecast_type]
        assert data_map is not None
        df = data_map[table]
        run_start = datetime.strptime(run_start, DATETIME_FORMAT)
        run_end = datetime.strptime(run_end, DATETIME_FORMAT)
        assert pd.Timestamp(df[runtime_col].unique()[0]) >= run_start
        assert pd.Timestamp(df[runtime_col].unique()[-1]) <= run_end


class TestToXarray:
    def test_two_datetime_cols_to_xarray(
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
        ) = TestCompileData.setup_compilation_test(
            TestCompileData(),
            gen_datetime,
            fix_forecasted_dt,
            forecast_type,
            time_delta,
        )
        data_map = compile_data(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            table,
            raw_cache=tmp_path,
            data_format="xr",
        )
        assert data_map is not None
        assert type(data_map[table]) is xr.Dataset
        assert len(data_map[table].dims.keys()) > 1

    def test_high_dimensionality_warning(self, caplog):
        df1 = pd.DataFrame(
            {"RUN_DATETIME": list(range(0, 400)), "b": list(range(0, 400))}
        )
        df2 = pd.DataFrame(
            {
                "RUN_DATETIME": list(range(0, 2)),
                "RUN_TYPE": list(range(0, 2)),
                "REGIONID": list(range(0, 2)),
                "DUID": list(range(0, 2)),
                "CONSTRAINTID": list(range(0, 2)),
                "INTERVAL_DATETIME": list(range(0, 2)),
            }
        )
        caplog.set_level(logging.WARNING)
        for df in (df1, df2):
            to_xarray(df, "STPASA")
        assert len(caplog.get_records("call")) == 2
        assert all(
            [
                (
                    "High-dimensional data. Large datetime requests may result "
                    + "in the Python process being killed by the system"
                )
                in record.msg
                for record in caplog.get_records("call")
            ]
        )
