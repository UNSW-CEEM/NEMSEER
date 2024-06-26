import logging
import pathlib
import shutil
from copy import deepcopy
from pathlib import Path
from zipfile import BadZipFile

import pytest
import requests

from nemseer.data import INVALID_STUBS_FILE, MMSDM_ARCHIVE_URL
from nemseer.downloader import (
    ForecastTypeDownloader,
    _construct_sqlloader_forecastdata_url,
    get_sqlloader_forecast_tables,
    get_sqlloader_years_and_months,
    get_unzipped_csv,
)
from nemseer.query import Query, generate_sqlloader_filenames


def test_standard_sqlloader_url():
    url = _construct_sqlloader_forecastdata_url(2021, 2, "STPASA", "REGIONSOLUTION")
    assert url == (
        MMSDM_ARCHIVE_URL
        + "2021/MMSDM_2021_02/MMSDM_Historical_Data_SQLLoader/DATA/"
        + "PUBLIC_DVD_STPASA_REGIONSOLUTION_202102010000.zip"
    )


def test_allmonths_available():
    years_months = get_sqlloader_years_and_months()
    test_index = int(len(years_months) / 2)
    all_months = list(range(1, 13))
    assert years_months[list(years_months.keys())[test_index]] == all_months


def test_tables_for_invalid_forecasttype(get_test_year_and_month):
    with pytest.raises(ValueError):
        get_sqlloader_forecast_tables(*get_test_year_and_month, "FAIL")


def test_table_fetch_for_p5min(get_test_year_and_month):
    p5tables = get_sqlloader_forecast_tables(*get_test_year_and_month, "P5MIN")
    assert set(p5tables) == set(
        [
            "CONSTRAINTSOLUTION",
            "CASESOLUTION",
            "REGIONSOLUTION",
            "UNITSOLUTION",
            "INTERCONNECTORSOLN",
        ]
    )


def test_table_fetch_for_pd(get_test_year_and_month):
    pdtables = get_sqlloader_forecast_tables(*get_test_year_and_month, "PREDISPATCH")
    assert set(pdtables) == set(
        [
            "CASESOLUTION",
            "CONSTRAINT",
            "CONSTRAINT_D",
            "INTERCONNECTORRES",
            "INTERCONNECTORRES_D",
            "INTERCONNECTR_SENS_D",
            "LOAD",
            "LOAD_D",
            "MNSPBIDTRK",
            "OFFERTRK",
            "PRICE",
            "PRICESENSITIVITIE_D",
            "PRICE_D",
            "REGIONSUM",
            "REGIONSUM_D",
            "SCENARIODEMAND",
            "SCENARIODEMANDTRK",
        ]
    )


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
        p5_to_check = set(
            [
                "CONSTRAINTSOLUTION1",
                "CONSTRAINTSOLUTION2",
                "CONSTRAINTSOLUTION3",
                "CONSTRAINTSOLUTION4",
            ]
        )
        pd_to_check = set(
            [
                "LOAD1",
                "LOAD2",
                "CONSTRAINT1",
                "CONSTRAINT2",
            ]
        )
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

    def test_casesolution_download_and_to_parquet(
        self, tmp_path, valid_download_datetimes
    ):
        for forecast_type in ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA"):
            query = self.casesolution_query(
                tmp_path, forecast_type, valid_download_datetimes
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
        new_query.tables.append("CASESOLUTION")
        downloader = ForecastTypeDownloader.from_Query(query)
        caplog.set_level(logging.INFO)
        downloader.download_csv()
        assert any(
            [
                record.msg
                for record in caplog.get_records("call")
                if "REGIONRESULT for 2/2021 in raw_cache" == record.msg
            ]
        )

    def test_skip_invalid_zip(self, caplog, tmp_path, valid_download_datetimes):
        query = self.valid_casesolution(tmp_path, valid_download_datetimes)
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
                if "PUBLIC_DVD_STPASA_CASESOLUTION_202102010000 previously found to be "
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
                if "PUBLIC_DVD_STPASA_CASESOLUTION_202102010000.parquet already exists"
                == record.msg
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

    def test_predisp_handling(self, tmp_path, valid_download_datetimes):
        predisp_all_query = self.predisp_all_query(tmp_path, valid_download_datetimes)
        predisp_d_query = self.predisp_d_query(tmp_path, valid_download_datetimes)
        for query in (predisp_d_query, predisp_all_query):
            downloader = ForecastTypeDownloader.from_Query(query)
            downloader.download_csv()
        path = pathlib.Path(tmp_path)
        assert len(list(path.iterdir())) == 2
        assert len(list(path.glob("*PRICE_D*.[Cc][Ss][Vv]"))) == 1
        assert len(list(path.glob("*PRICE*.[Cc][Ss][Vv]"))) == 2
