import datetime
import logging
import pathlib
import shutil
import zoneinfo
from copy import deepcopy
from pathlib import Path
from zipfile import BadZipFile

import pytest
import requests

from nemseer.data import INVALID_STUBS_FILE
from nemseer.downloader import (
    ForecastTypeDownloader,
    _construct_sqlloader_forecastdata_url,
    get_sqlloader_forecast_tables,
    get_sqlloader_years_and_months,
    get_unzipped_csv,
    get_wait_seconds,
)
from nemseer.query import Query, generate_sqlloader_filenames


def test_standard_sqlloader_url():
    url = _construct_sqlloader_forecastdata_url(2021, 2, "STPASA", "REGIONSOLUTION")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        + "2021/MMSDM_2021_02/MMSDM_Historical_Data_SQLLoader/DATA/"
        + "PUBLIC_DVD_STPASA_REGIONSOLUTION_202102010000.zip"
    )
    url = _construct_sqlloader_forecastdata_url(2024, 7, "STPASA", "REGIONSOLUTION")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2024/MMSDM_2024_07/MMSDM_Historical_Data_SQLLoader/DATA/"
        "PUBLIC_DVD_STPASA_REGIONSOLUTION_202407010000.zip"
    )
    url = _construct_sqlloader_forecastdata_url(2024, 8, "STPASA", "REGIONSOLUTION")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2024/MMSDM_2024_08/MMSDM_Historical_Data_SQLLoader/DATA/"
        "PUBLIC_ARCHIVE%2523STPASA_REGIONSOLUTION%2523FILE01%2523202408010000.zip"
    )
    url = _construct_sqlloader_forecastdata_url(2025, 3, "P5MIN", "CASESOLUTION")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2025/MMSDM_2025_03/MMSDM_Historical_Data_SQLLoader/DATA/"
        "PUBLIC_ARCHIVE%2523P5MIN_CASESOLUTION%2523FILE01%2523202503010000.zip"
    )
    url = _construct_sqlloader_forecastdata_url(2026, 1, "PREDISPATCH", "MNSPBIDTRK")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2026/MMSDM_2026_01/MMSDM_Historical_Data_SQLLoader/DATA/"
        "PUBLIC_ARCHIVE%2523PREDISPATCH_MNSPBIDTRK%2523FILE01%2523202601010000.zip"
    )
    url = _construct_sqlloader_forecastdata_url(2026, 4, "PREDISPATCH", "REGIONSUM")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2026/MMSDM_2026_04/MMSDM_Historical_Data_SQLLoader/PREDISP_ALL_DATA/"
        "PUBLIC_ARCHIVE%2523PREDISPATCHREGIONSUM%2523ALL%2523FILE01%2523202604010000"
        ".zip"
    )
    url = _construct_sqlloader_forecastdata_url(2026, 3, "PREDISPATCH", "OFFERTRK")
    assert url == (
        "https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
        "2026/MMSDM_2026_03/MMSDM_Historical_Data_SQLLoader/DATA/"
        "PUBLIC_ARCHIVE%2523PREDISPATCHOFFERTRK%2523FILE01%2523202603010000.zip"
    )


def test_get_wait_seconds():
    class HeaderHolder:
        headers = dict()

    response = HeaderHolder()
    assert get_wait_seconds(response, 3) == 8
    response.headers["Retry-After"] = "1"
    assert get_wait_seconds(response, 2) == 1
    in_20s = datetime.datetime.now(zoneinfo.ZoneInfo("UTC")) + datetime.timedelta(
        seconds=20
    )
    response.headers["Retry-After"] = in_20s.strftime("%a, %d %b %Y %H:%M:%S GMT")
    assert get_wait_seconds(response, 5) == pytest.approx(20, abs=1)
    in_30s = datetime.datetime.now(zoneinfo.ZoneInfo("UTC")) + datetime.timedelta(
        seconds=30
    )
    response.headers["Retry-After"] = in_30s.strftime("%A, %d %b %Y %H:%M:%S %Z")
    assert get_wait_seconds(response, 5) == pytest.approx(30, abs=1)


@pytest.mark.slow
def test_allmonths_available():
    years_months = get_sqlloader_years_and_months()
    test_index = int(len(years_months) / 2)
    all_months = list(range(1, 13))
    assert years_months[list(years_months.keys())[test_index]] == all_months


def test_tables_for_invalid_forecasttype(get_test_year_and_month):
    with pytest.raises(ValueError):
        get_sqlloader_forecast_tables(*get_test_year_and_month, "FAIL")


@pytest.mark.parametrize(
    ("year", "month", "extra_tables"),
    (
        (2015, 1, {"UNITSOLUTION"}),
        (2020, 2, {"UNITSOLUTION"}),
        (2024, 7, {"UNITSOLUTION", "SCENARIODEMAND", "SCENARIODEMANDTRK"}),
        (
            2024,
            8,
            {
                "INTERSENSITIVITIES",
                "PRICESENSITIVITIES",
                "SCENARIODEMAND",
                "SCENARIODEMANDTRK",
                "LOCAL_PRICE",
            },
        ),
        (
            2025,
            12,
            {
                "BLOCKEDCONSTRAINT",
                "INTERSENSITIVITIES",
                "PRICESENSITIVITIES",
                "SCENARIODEMAND",
                "SCENARIODEMANDTRK",
                "FCAS_REQ_RUN",
                "FCAS_REQ_CONSTRAINT",
                "LOCAL_PRICE",
            },
        ),
    ),
)
def test_table_fetch_for_p5min(year: int, month: int, extra_tables: set[str]):
    base_tables = {
        "CONSTRAINTSOLUTION",
        "CASESOLUTION",
        "REGIONSOLUTION",
        "INTERCONNECTORSOLN",
    }
    expected_tables = base_tables | extra_tables
    p5tables = get_sqlloader_forecast_tables(
        year=year, month=month, forecast_type="P5MIN"
    )
    assert set(p5tables) == expected_tables


@pytest.mark.parametrize(
    ("year", "month", "extra_tables"),
    (
        (2015, 1, set()),
        (2020, 2, set()),
        (2024, 7, set()),
        (2024, 8, {"PRICESENSITIVITIES", "LOCAL_PRICE", "FCAS_REQ"}),
        (2025, 12, {"BLOCKEDCONSTRAINT", "PRICESENSITIVITIES", "LOCAL_PRICE"}),
    ),
)
def test_table_fetch_for_pd(year: int, month: int, extra_tables: set[str]):
    base_tables = {
        "CASESOLUTION",
        "CONSTRAINT",
        "INTERCONNECTORRES",
        "LOAD",
        "MNSPBIDTRK",
        "OFFERTRK",
        "PRICE",
        "REGIONSUM",
        "SCENARIODEMAND",
        "SCENARIODEMANDTRK",
    }
    expected_tables = base_tables | extra_tables
    pdtables = get_sqlloader_forecast_tables(
        year=year, month=month, forecast_type="PREDISPATCH"
    )
    # we don't care for tables that end in _D because they only exist prior to Aug 2024
    set_pd_tables = set(t for t in pdtables if not t.endswith("_D"))
    assert set_pd_tables == expected_tables


class TestForecastTypeDownloader:
    def valid_query(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "STPASA",
            "REGIONSOLUTION",
            raw_cache=raw_cache,
        )

    def valid_casesolution(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "STPASA",
            "CASESOLUTION",
            raw_cache=raw_cache,
        )

    def invalid_tables_query(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "P5MIN",
            ["DISPATCHLOAD", "REGIONDISPATCHSUM"],
            raw_cache=raw_cache,
        )

    def constraint_solution_query_p5min(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "P5MIN",
            "CONSTRAINTSOLUTION",
            raw_cache=raw_cache,
        )

    def constraint_solution_query_pd(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "PREDISPATCH",
            ["CONSTRAINT", "LOAD"],
            raw_cache=raw_cache,
        )

    def casesolution_query(self, raw_cache, forecast_type, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            forecast_type,
            "CASESOLUTION",
            raw_cache=raw_cache,
        )

    def predisp_all_query(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "PREDISPATCH",
            "PRICE",
            raw_cache=raw_cache,
        )

    def predisp_d_query(self, raw_cache, valid_download_datetimes):
        (
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
        ) = valid_download_datetimes
        return Query.initialise(
            run_start,
            run_end,
            forecasted_start,
            forecasted_end,
            "PREDISPATCH",
            "PRICE_D",
            raw_cache=raw_cache,
        )

    def test_invalid_tables(self, tmp_path, valid_download_datetimes):
        with pytest.raises(ValueError):
            ForecastTypeDownloader.from_Query(
                self.invalid_tables_query(tmp_path, valid_download_datetimes)
            )

    def test_table_enumeration(self, tmp_path, valid_download_datetimes):
        """
        Add other initialisations if additional tables require enumeration
        """
        ftd_p5 = ForecastTypeDownloader.from_Query(
            self.constraint_solution_query_p5min(tmp_path, valid_download_datetimes)
        )
        ftd_pd = ForecastTypeDownloader.from_Query(
            self.constraint_solution_query_pd(tmp_path, valid_download_datetimes)
        )
        p5_to_check = {"CONSTRAINTSOLUTION"}
        pd_to_check = {"LOAD", "CONSTRAINT"}
        assert p5_to_check.issubset(set(ftd_p5.tables))
        assert pd_to_check.issubset(set(ftd_pd.tables))

    def test_raise_on_bad_url(self, tmp_path):
        with pytest.raises(requests.exceptions.HTTPError):
            bad_url = (
                "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
                + "2021/MMSDM_2021_04/MMSDM_Historical_Data_SQLLoader/PREDISP_ALL_DATA"
                + "PUBLIC_DVD_PREDISPATCHINTERCONNECTORRES_202104010000.zip"
            )
            get_unzipped_csv(bad_url, tmp_path)

    @pytest.mark.slow
    def test_casesolution_download_and_to_parquet(
        self, tmp_path, valid_download_datetimes_pre202408
    ):
        """Test that CASESOLUTION can be retrieved for each of the five forecast types.

        After Aug 2024 AEMO stopped publishing CASESOLUTION for MTPASA.
        """
        for forecast_type in ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA"):
            query = self.casesolution_query(
                tmp_path, forecast_type, valid_download_datetimes_pre202408
            )
            downloader = ForecastTypeDownloader.from_Query(query)
            downloader.download_csv()
            downloader.convert_to_parquet()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 5
        assert all([True for file in path.iterdir() if "CASESOLUTION" in file.name])
        assert all([True for file in path.iterdir() if ".parquet" in file.name])

    def test_skip_existing_component_of_query(self, caplog, download_file_to_cache):
        query = download_file_to_cache
        new_query = deepcopy(query)
        new_query.tables.append("CASERESULT")
        caplog.set_level(logging.INFO)
        downloader = ForecastTypeDownloader.from_Query(query)
        downloader.download_csv()
        downloader = ForecastTypeDownloader.from_Query(new_query)
        downloader.download_csv()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "REGIONRESULT  for 2/2025 in raw_cache" == record.msg
            ]
        )

    @pytest.mark.parametrize(
        ("year", "month", "expected"),
        (
            (2021, 2, "PUBLIC_DVD_STPASA_CASESOLUTION_202102010000"),
            (
                2024,
                8,
                "PUBLIC_ARCHIVE%2523STPASA_CASESOLUTION%2523FILE01%2523202408010000",
            ),
        ),
    )
    def test_skip_invalid_zip(self, caplog, tmp_path, year, month, expected):
        run_start = f"{year}/{month:0>2d}/01 00:00"
        run_end = f"{year}/{month:0>2d}/05 00:00"
        forecasted_start = f"{year}/{month:0>2d}/08 00:00"
        forecasted_end = f"{year}/{month:0>2d}/08 23:55"
        query = self.valid_casesolution(
            tmp_path, (run_start, run_end, forecasted_start, forecasted_end)
        )
        stubfile = query.raw_cache / INVALID_STUBS_FILE
        fnames = generate_sqlloader_filenames(
            query.run_start, query.run_end, query.forecast_type, query.tables
        ).values()
        with open(stubfile, "x") as f:
            for fn in fnames:
                f.write(f"{fn}\n")
        downloader = ForecastTypeDownloader.from_Query(query)
        caplog.set_level(logging.WARNING)
        downloader.download_csv()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if f"{expected} previously found to be "
                + "invalid/corrupted. Skipping download for this file."
                in record.msg
            ]
        )

    def test_parquet_conversion_short_circuit(
        self, caplog, tmp_path, valid_download_datetimes
    ):
        downloader = ForecastTypeDownloader.from_Query(
            self.valid_casesolution(tmp_path, valid_download_datetimes)
        )
        caplog.set_level(logging.INFO)
        downloader.download_csv()
        downloader.convert_to_parquet(keep_csv=True)
        downloader.convert_to_parquet()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "PUBLIC_ARCHIVE#STPASA_CASESOLUTION#FILE01#202502010000.parquet"
                " already exists" == record.msg
            ]
        )

    def test_only_convert_forecast_csvs(self, tmp_path, valid_download_datetimes):
        downloader = ForecastTypeDownloader.from_Query(
            self.valid_casesolution(tmp_path, valid_download_datetimes)
        )
        downloader.download_csv()
        csv = list(Path(tmp_path).glob("*.[Cc][Ss][Vv]"))[0]
        mock_nemosis_csv = csv.with_name("PUBLIC_DVD_DISPATCHLOAD_201312010000.CSV")
        shutil.copy(csv, mock_nemosis_csv)
        downloader.convert_to_parquet()
        assert (
            list(Path(tmp_path).glob("*.[Cc][Ss][Vv]"))[0].name
            == "PUBLIC_DVD_DISPATCHLOAD_201312010000.CSV"
        )
        assert len(list(Path(tmp_path).glob("*.parquet"))) == 1

    def test_bad_zipfile_handling(self, tmp_path, mocker, valid_download_datetimes):
        def mock_extractall(self, raw_cache):
            raise BadZipFile

        mocker.patch("nemseer.downloader.ZipFile.extractall", mock_extractall)
        query = self.casesolution_query(tmp_path, "STPASA", valid_download_datetimes)
        downloader = ForecastTypeDownloader.from_Query(query)
        downloader.download_csv()
        with open(tmp_path / INVALID_STUBS_FILE, "r") as f:
            line = f.readline()
        assert not line == "PUBLIC_DVD_STPASA_CASESOLUTION_202102010000"

    def test_predisp_handling(self, tmp_path, valid_download_datetimes_pre202408):
        # PRICE_D tables don't exist for post 202408 so only test with pre Aug 2024
        predisp_all_query = self.predisp_all_query(
            tmp_path, valid_download_datetimes_pre202408
        )
        predisp_d_query = self.predisp_d_query(
            tmp_path, valid_download_datetimes_pre202408
        )
        for query in (predisp_d_query, predisp_all_query):
            downloader = ForecastTypeDownloader.from_Query(query)
            downloader.download_csv()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 2
        assert len(list(path.glob("*PRICE_D*.[Cc][Ss][Vv]"))) == 1
        assert len(list(path.glob("*PRICE*.[Cc][Ss][Vv]"))) == 2
