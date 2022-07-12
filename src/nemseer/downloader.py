from attrs import define, field
from datetime import datetime
from typing import List, Optional, Union

from .dl_helpers.urls import MMSDM_ARCHIVE_URL
from .loader import Loader


@define(kw_only=True)
class ForecastTypeDownloader:
    forecast_start: datetime
    forecast_end: datetime
    forecast_type: str
    tables: Union[str, List[str]]
    raw_cache: Optional[str] = field(default=None)

    @classmethod
    def from_Loader(cls, loader: Loader):
        return cls(forecast_start=loader.forecast_start,
                   forecast_end=loader.forecast_end,
                   forecast_type=loader.forecast_type, tables=loader.tables,
                   raw_cache=loader.raw_cache)
