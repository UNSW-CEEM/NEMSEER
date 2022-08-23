import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

from attrs import define

from .data import ENUMERATED_TABLES
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
        forecast_type: `MTPASA`, `STPASA`, `PDPASA`, `PREDISPATCH` or `P5MIN`.
        tables: Tables queried.
    Returns:
        A dictionary mapping the queried table name to filenames associated with that
        queried table.
    """
    metadata_to_filename = generate_sqlloader_filenames(
        forecast_start, forecast_end, forecast_type, tables
    )
    table_file_map = {}
    for table in tables:
        filenames_to_map = list()
        for metadata in metadata_to_filename.keys():
            if metadata[2] == table:
                filenames_to_map.append(metadata_to_filename[metadata])
        table_file_map[table] = filenames_to_map
    return table_file_map


@define
class DataCompiler:
    """`DataCompiler` compiles data"""

    run_start: datetime
    run_end: datetime
    forecasted_start: datetime
    forecasted_end: datetime
    forecast_type: str
    tables: List[str]
    metadata: Dict
    raw_cache: Path
    processed_cache: Union[None, Path]

    @classmethod
    def from_Query(cls, query: Query) -> "DataCompiler":
        """Constructor method for DataCompiler from Query."""
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
        )

    def compile_raw_data(self):
        """"""
