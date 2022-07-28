# read version from installed package
import logging
import sys
from importlib.metadata import version

from .nemseer import download_raw_data

__version__ = version("nemseer")

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)

__all__ = [
    "download_raw_data",
]
