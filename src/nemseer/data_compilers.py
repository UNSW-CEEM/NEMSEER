import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Union

import pandas as pd
import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore
import xarray as xr
from attrs import define, field

from .data import ENUMERATED_TABLES, INVALID_STUBS_FILE
from .data_handlers import apply_run_and_forecasted_time_filters, to_xarray
from .forecast_type.validators import (
    validate_MTPASA_datetime_inputs,
    validate_P5MIN_datetime_inputs,
    validate_PDPASA_datetime_inputs,
    validate_PREDISPATCH_datetime_inputs,
    validate_STPASA_datetime_inputs,
)
from .query import Query, _enumerate_tables, generate_sqlloader_filenames

logger = logging.getLogger(__name__)


def _map_files_to_table(
    run_start: datetime,
    run_end: datetime,
    forecast_type: str,
    tables: List[str],
) -> Dict[str, List[str]]:
    """Maps filenames of interest to each queried table

    Translates output from `generate_sqlloader_filenames` to map filenames of interest
    to a queried table name.

    Handles enumerated tables (e.g. `PREDISP_ALL_DATA`) by mapping enumerated filenames
    to non-enumerated table type (which is used in the user query).
    E.g. '...PREDISPATCHLOAD1' and '...PREDISPATCHLOAD2' mapped to 'LOAD'

    Args:
        forecast_start: Forecasts made at or after this datetime are queried.
        forecast_end: Forecasts made before or at this datetime are queried.
        forecast_type: One of :data:`nemseer.forecast_types`
        tables: Tables queried.
    Returns:
        A dictionary mapping the queried table name to filenames associated with that
        queried table.
    """
    metadata_to_filename = generate_sqlloader_filenames(
        run_start, run_end, forecast_type, tables
    )
    if forecast_type in ENUMERATED_TABLES.keys():
        enumerated_tables = [pair[0] for pair in ENUMERATED_TABLES[forecast_type]]
    else:
        enumerated_tables = []
    table_file_map: Dict[str, List[str]] = {}
    for table in tables:
        filenames_to_map = list()
        for metadata in metadata_to_filename.keys():
            if metadata[2] == table:
                filenames_to_map.append(metadata_to_filename[metadata])
        if (enum_base := re.match(r"([A-Z]*)[0-9]", table)) and enum_base.group(
            1
        ) in enumerated_tables:
            map_table_name = enum_base.group(1)
            if map_table_name in table_file_map.keys():
                table_file_map[map_table_name].extend(filenames_to_map)
            else:
                table_file_map[map_table_name] = filenames_to_map
        else:
            table_file_map[table] = filenames_to_map
    return table_file_map


def _input_datetime_validation(instance, attribute, value) -> None:
    """Dispatches the correct datetime validator based on the :term:`forecast_type`"""
    validator_map = {
        "P5MIN": validate_P5MIN_datetime_inputs,
        "PREDISPATCH": validate_PREDISPATCH_datetime_inputs,
        "PDPASA": validate_PDPASA_datetime_inputs,
        "STPASA": validate_STPASA_datetime_inputs,
        "MTPASA": validate_MTPASA_datetime_inputs,
    }
    validator_func = validator_map[instance.forecast_type]
    validator_func(
        instance.run_start,
        instance.run_end,
        instance.forecasted_start,
        instance.forecasted_end,
    )
    return None


@define
class DataCompiler:
    """:class:`DataCompiler` compiles data from the :term:`raw_cache` or
    :term:`processed_cache`.

    Attributes:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
        forecast_type: One of :data:`nemseer.forecast_types`.
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        metadata: Metadata dictionary. Constructed by
            :meth:`Query.initialise() <nemseer.query.Query.initialise()>`.
        raw_cache (optional): Path to build or reuse :term:`raw_cache`.
        processed_cache (optional): Path to build or reuse :term`processed cache`.
            Should be distinct from :attr:`raw_cache`
        processed_queries: Defaults to :class:`None` on initialisation.
        raw_table: Populated via :meth:`DataCompiler.from_Query`
        compiled_data: Defaults to :class:`None` on initialisation. Populated once data
            is compiled by methods.
    """

    run_start: datetime = field(validator=_input_datetime_validation)
    run_end: datetime
    forecasted_start: datetime
    forecasted_end: datetime
    forecast_type: str
    metadata: Dict[str, str]
    raw_cache: Path
    processed_cache: Union[None, Path]
    processed_queries: Union[Dict[str, Path], Dict]
    raw_tables: List[str]
    compiled_data: Union[None, Dict[str, pd.DataFrame], Dict[str, xr.Dataset]] = field(
        default=None
    )

    @classmethod
    def from_Query(cls, query: Query) -> "DataCompiler":
        """Constructor method for :class:`DataCompiler` from
        :class:`Query <nemseer.query.Query>`."""
        tables = query.tables
        if query.processed_cache:
            if query.processed_queries:
                raw_tables = list(set(tables) - set(query.processed_queries.keys()))
            else:
                raw_tables = tables
        else:
            raw_tables = tables
        for ftype in ENUMERATED_TABLES:
            if query.forecast_type == ftype:
                for table, enumerate_to in ENUMERATED_TABLES[ftype]:
                    if table in raw_tables:
                        tables = _enumerate_tables(tables, table, enumerate_to)
        return cls(
            query.run_start,
            query.run_end,
            query.forecasted_start,
            query.forecasted_end,
            query.forecast_type,
            query.metadata,
            query.raw_cache,
            query.processed_cache,
            query.processed_queries,
            raw_tables,
            None,
        )

    def invalid_or_corrupted_files(self) -> List[str]:
        """A list of invalid/corrupted files as per files in `.invalid_aemo_files.txt`.
        Returns an empty list if the stubfile does not exist.
        """
        invalid_or_corrupted_stubfile = self.raw_cache / Path(INVALID_STUBS_FILE)
        if invalid_or_corrupted_stubfile.exists():
            with open(invalid_or_corrupted_stubfile, "r") as f:
                invalid_or_corrupted = f.readlines()
            check_files = [f.strip() for f in invalid_or_corrupted]
            return check_files
        else:
            return []

    def compile_raw_data(self, data_format: str = "df") -> None:
        """Compiles data from :attr:`raw_cache` to a :class:`pandas.DataFrame` (default)
        or to a :class:`xarray.Dataset`.

        This compiler will:

        - Skip invalid/corrupted files as recorded in `.invalid_aemo_files.txt`
        - Read :term:`raw_cache` parquet files and apply datetime filtering
        - Convert :class:`DataFrame <pandas.DataFrame>` to :class:`xarray.Dataset`
          (if :attr:`data_format` = "xr")
        - Update :attr:`compiled_data`

        Args:
            data_format: Default "df" (:class:`pandas.DataFrame`). Other valid input is
                "xr", which returns :class:`xarray.Dataset`.
        Warning:
            Skips any files previously found to be invalid/corrupted and prints a
            warning
        """
        file_to_table_map = _map_files_to_table(
            self.run_start, self.run_end, self.forecast_type, self.raw_tables
        )
        table_to_data_map = {}
        invalid_files = self.invalid_or_corrupted_files()
        for table in file_to_table_map.keys():
            files = file_to_table_map[table]
            filtered_files = [file for file in files if file not in invalid_files]
            if not filtered_files:
                raise ValueError(
                    "Query failed as all files to be compiled were found to be"
                    + " invalid/corrupt on previous download. You can force nemseer"
                    + " to load these files by deleting them from "
                    + ".invalid_aemo_files.txt"
                )
            elif len(filtered_files) < len(files):
                logger.warning(
                    "Some files not compiled as these were found to be"
                    + " invalid/corrupt on previous download. You can force nemseer"
                    + " to load these files by deleting them from "
                    + ".invalid_aemo_files.txt"
                )
            dfs = []
            for file in filtered_files:
                filepath = self.raw_cache / Path(f"{file}.parquet")
                df = pd.read_parquet(filepath)
                df = apply_run_and_forecasted_time_filters(
                    df,
                    self.run_start,
                    self.run_end,
                    self.forecasted_start,
                    self.forecasted_end,
                    self.forecast_type,
                )
                dfs.append(df.reset_index(drop=True))
            concat_df = pd.concat(dfs)
            if any(concat_df.duplicated()):
                logger.warning(
                    "Duplicate rows detected whilst concatenating data. "
                    + "Dropping these rows."
                )
                concat_df = concat_df.drop_duplicates()
            if data_format == "xr":
                logger.info(f"Converting {table} data to xarray.")
                concat_data = to_xarray(concat_df, self.forecast_type)
            else:
                concat_data = concat_df
            table_to_data_map[table] = concat_data

        if not self.compiled_data:
            self.compiled_data = table_to_data_map
        else:
            self.compiled_data.update(table_to_data_map)

    def compile_processed_data(self, data_format: str = "df") -> None:
        """Compiles data from the :attr:`processed_cache`, as per entries in
        :attr:`processed_queries`, to a :class:`pandas.DataFrame` (default) or to a
        :class:`xarray.Dataset`.

        This method will update :attr:`compiled_data`.

        Args:
            data_format: Default "df" (:class:`pandas.DataFrame`). Other valid input
                is "xr", which compiles :class:`xarray.Dataset`.
        """
        read_fn: Dict[str, Callable] = {
            "df": pd.read_parquet,
            "xr": xr.open_dataset,
        }
        processed_data = {}
        if not self.processed_queries:
            pass
        else:
            for table in self.processed_queries:
                file = self.processed_queries[table]
                logger.info(f"Compiling {table} data from the processed cache")
                data = read_fn[data_format](file)
                processed_data[table] = data
            if not self.compiled_data:
                self.compiled_data = processed_data
            else:
                self.compiled_data.update(processed_data)

    def write_to_processed_cache(self) -> None:
        """Writes netCDF4 for :class:`xarray.Dataset` and parquet
        for :class:`pandas.DataFrame` to the :attr:`processed_cache` with associated
        query metadata.

        Note that parquet metadata needs to be UTF-8 encoded.

        Raises:
            ValueError: If :attr:`processed_cache` is :class:`None`, or if
                :attr:`compiled_data` contains data that is neither all
                :class:`pandas.DataFrame` or all :class:`xarray.Dataset`
            IOError: If :attr:`compiled_data` is :class:`None`
        """

        def _df_to_pyarrow_with_metadata(
            df: pd.DataFrame, metadata: Dict[str, str]
        ) -> pa.Table:
            """Converts DataFrame to pyarrow Table so that metadata can be added.
            Args:
                df: pandas DataFrame
                metadata: :class:`dict` built by
                    :classmethod:`nemseer.query.Query.initialise()`
            Returns:
                pyarrow Table with schema and nemseer metadata encoded as a b-string
            """
            table = pa.Table.from_pandas(df)
            pandas_metadata = table.schema.metadata
            nemseer_metadata = {b"nemseer": str(metadata).encode()}
            merged_metadata = {**pandas_metadata, **nemseer_metadata}
            table = table.replace_schema_metadata(merged_metadata)
            return table

        def _build_query_filename(compiler: DataCompiler, table: str) -> str:
            """Builds a filename based on a table name and query details.

            Args:
                compiler: DataCompiler instance with populated query info
                table: Specific table to build a filename for
            Returns
                A filename constructed based on query details.
            """
            (fs, fe) = (compiler.forecasted_start, compiler.forecasted_end)
            (rs, re) = (compiler.run_start, compiler.run_end)
            rs_re = (
                f"{rs.year}{rs.month}{rs.day}{rs.hour}{rs.minute}"
                + "_"
                + f"{re.year}{re.month}{re.day}{re.hour}{re.minute}"
            )
            fs_fe = (
                f"{fs.year}{fs.month}{fs.day}{fs.hour}{fs.minute}"
                + "_"
                + f"{fe.year}{fe.month}{fe.day}{fe.hour}{fe.minute}"
            )
            fn = f"{compiler.forecast_type}_{table}_{rs_re}_{fs_fe}"
            return fn

        if self.processed_cache is None:
            raise ValueError(
                "Writing to processed cache requires that the processed cache "
                + "be specified"
            )
        if self.compiled_data is None:
            raise IOError("No compiled data to write to processed cache")
        data = self.compiled_data
        xrbool = all([type(data) is xr.Dataset for data in self.compiled_data.values()])
        dfbool = all(
            [type(data) is pd.DataFrame for data in self.compiled_data.values()]
        )
        for table in data.keys():
            if self.processed_queries and table in self.processed_queries.keys():
                continue
            else:
                fn = _build_query_filename(self, table)
                self.metadata.update({"table": table})
                dataset = data[table]
                if xrbool:
                    fn_path = self.processed_cache / Path(fn + ".nc")
                    dataset.attrs = self.metadata  # type: ignore
                    logger.info(f"Writing {table} to the processed cache as netCDF")
                    dataset.to_netcdf(fn_path)  # type: ignore
                elif dfbool:
                    fn_path = self.processed_cache / Path(fn + ".parquet")
                    pyarrow_table = _df_to_pyarrow_with_metadata(
                        dataset, self.metadata  # type: ignore
                    )
                    logger.info(f"Writing {table} to the processed cache as parquet")
                    pq.write_table(pyarrow_table, fn_path)
                else:
                    raise ValueError(
                        "Compiled data is not in a valid data structure. "
                        + "Compiled data should be in a pandas DataFrame or "
                        + "xarray Dataset"
                    )
