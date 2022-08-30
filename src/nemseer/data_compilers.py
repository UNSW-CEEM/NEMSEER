import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd
from attrs import define, field

from .data import ENUMERATED_TABLES, INVALID_STUBS_FILE
from .data_handlers import apply_run_and_forecasted_time_filters
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
    table_file_map = {}
    for table in tables:
        filenames_to_map = list()
        for metadata in metadata_to_filename.keys():
            if metadata[2] == table:
                filenames_to_map.append(metadata_to_filename[metadata])
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
        compiled_data: Defaults to `None` on initialisation. Populated once data
            is compiled by methods.
    """

    run_start: datetime = field(validator=_input_datetime_validation)
    run_end: datetime
    forecasted_start: datetime
    forecasted_end: datetime
    forecast_type: str
    tables: List[str]
    metadata: Dict
    raw_cache: Path
    processed_cache: Union[None, Path]
    compiled_data: Union[None, Dict[str, pd.DataFrame]] = field(default=None)

    @classmethod
    def from_Query(cls, query: Query) -> "DataCompiler":
        """Constructor method for :class:`DataCompiler` from
        :class:`Query <nemseer.query.Query>`."""
        tables = query.tables
        for ftype in ENUMERATED_TABLES:
            if query.forecast_type == ftype:
                for table, enumerate_to in ENUMERATED_TABLES[ftype]:
                    if table in tables:
                        tables = _enumerate_tables(tables, table, enumerate_to)
        if hasattr(query, "processed_cache"):
            processed_cache = query.processed_cache
        else:
            processed_cache = None
        return cls(
            run_start=query.run_start,
            run_end=query.run_end,
            forecasted_start=query.forecasted_start,
            forecasted_end=query.forecasted_end,
            forecast_type=query.forecast_type,
            tables=tables,
            metadata=query.metadata,
            raw_cache=query.raw_cache,
            processed_cache=processed_cache,
            compiled_data=None,
        )

    def invalid_or_corrupted_files(self) -> List[str]:
        """

        Todo:
            Make stubfile a constant in data
        """
        invalid_or_corrupted_stubfile = self.raw_cache / Path(INVALID_STUBS_FILE)
        if invalid_or_corrupted_stubfile.exists():
            with open(invalid_or_corrupted_stubfile, "r") as f:
                invalid_or_corrupted = f.readlines()
            check_files = [f.strip() for f in invalid_or_corrupted]
            return check_files
        else:
            return []

    def compile_raw_data(self):
        """"""
        file_to_table_map = _map_files_to_table(
            self.run_start, self.run_end, self.forecast_type, self.tables
        )
        table_to_df_map = {}
        invalid_files = self.invalid_or_corrupted_files()
        for table in file_to_table_map.keys():
            files = file_to_table_map[table]
            filtered_files = [file for file in files if file not in invalid_files]
            if len(filtered_files) < len(files):
                logging.warning(
                    "Some files not compiled as these were found to be"
                    + " invalid/corrupt on previous download. You can force nemseer"
                    + " to load this file by deleting it from "
                    + ".invalid_aemo_files.txt"
                )
            dfs = []
            for file in filtered_files:
                filepath = self.raw_cache / Path(f"{file}.parquet")
                df = pd.read_parquet(filepath)
                df = apply_run_and_forecasted_time_filters(
                    df,
                    self.forecast_type,
                    self.run_start,
                    self.run_end,
                    self.forecasted_start,
                    self.forecasted_end,
                )
                dfs.append(df)
            if len(dfs) == 1:
                table_to_df_map[table] = dfs.pop()
            else:
                table_to_df_map[table] = pd.concat(dfs, axis=0)
        self.compiled_data = table_to_df_map
