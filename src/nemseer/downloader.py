from attrs import define, field
from datetime import datetime
from typing import List, Optional, Union

from .dl_helpers.funcs import _construct_mmsdm_yearmonth_url
from .dl_helpers.urls import MMSDM_ARCHIVE_URL
from .loader import Loader


def _enumerate_tables(tables: List[str], table_str: str, range_to: int):
    """ Given a table name, populates a list with enumerated table names

    For example, given 'CONSTRAINTSOLUTION' and `range_to`=3, will populate
    `tables` with ['CONSTRAINTSOLUTION1',...,'CONSTRAINTSOLUTION3'].
    
    Args:
        tables: Table list
        table_str: Table string to enumerate
        range_to: Integer to enumerate to
    Returns:
        `tables` with enumerated `table_str`
    """
    tables.remove(table_str)
    for i in range(1, range_to + 1):
        tables.append(f"{table_str}{i}")
    return tables


@define(kw_only=True)
class ForecastTypeDownloader:
    forecast_start: datetime
    forecast_end: datetime
    forecast_type: str
    tables: Union[str, List[str]]
    raw_cache: Optional[str] = field(default=None)

    @classmethod
    def from_Loader(cls, loader: Loader):
        tables = loader.tables
        if "CONSTRAINTSOLUTION" in tables:
            tables = _enumerate_tables(tables, "CONSTRAINTSOLUTION", 4)
        return cls(forecast_start=loader.forecast_start,
                   forecast_end=loader.forecast_end,
                   forecast_type=loader.forecast_type, tables=tables,
                   raw_cache=loader.raw_cache)
    
