# read version from installed package
import logging
import sys
from importlib.metadata import version

# aliases for SQLLoader functions
from .dl_helpers.functions import get_sqlloader_forecast_tables as get_tables
from .dl_helpers.functions import get_sqlloader_years_and_months as get_data_daterange
from .nemseer import download_raw_data

__version__ = version("nemseer")

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)

__all__ = ["download_raw_data", "get_tables", "get_data_daterange"]
