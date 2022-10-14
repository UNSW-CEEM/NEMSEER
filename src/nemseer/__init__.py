# read version from installed package
import logging
import sys
import warnings
from importlib.metadata import version

# aliases for SQLLoader functions
from .data import FORECAST_TYPES as forecast_types
from .downloader import get_sqlloader_forecast_tables as get_tables
from .downloader import get_sqlloader_years_and_months as get_data_daterange
from .forecast_type.run_time_generators import generate_runtimes
from .nemseer import compile_data, download_raw_data

__version__ = version("nemseer")

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)

warnings.simplefilter(action="ignore", category=FutureWarning)

__all__ = [
    "compile_data",
    "download_raw_data",
    "get_tables",
    "get_data_daterange",
    "generate_runtimes",
    "forecast_types",
]
