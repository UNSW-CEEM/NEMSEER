# read version from installed package
import sys
from importlib.metadata import version

__version__ = version("nemseer")

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)
