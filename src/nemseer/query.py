import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from attrs import converters, define, field, validators
from dateutil import rrule

logger = logging.getLogger(__name__)


def _dt_converter(value: str) -> datetime:
    """Convert string to datetime.

    Args:
        value: String with format %d/%m/%Y %H:%M
    Returns:
        Datetime object
    """
    try:
        format = "%d/%m/%Y %H:%M"
        return datetime.strptime(value, format)
    except ValueError:
        raise ValueError("Datetime should be provided as follows: dd/mm/yyyy hh:mm")


def _tablestr_converter(value: Union[str, List[str]]) -> List[str]:
    """Returns a list of table strings, even if a single string is provided

    Args:
        value: Table string or list of table strings
    Returns:
        List of strings
    """
    if type(value) is str:
        return [value]
    else:
        return list(value)


def _validate_forecast_chronology(instance, attribute, value):
    """Validates forecast_start against forecast_end"""
    if value > instance.forecast_end:
        raise ValueError(
            "Forecast end datetime must be greater than or equal to"
            + " forecast start datetime."
        )


def _validate_forecasted_chronology(instance, attribute, value):
    """Validated forecasted_start against forecasted_end"""
    if value > instance.forecasted_end:
        raise ValueError(
            "Forecasted end datetime must be greater than or equal to"
            + " forecasted start datetime."
        )


def _validate_relative_chronology(instance, attribute, value):
    """Validates forecast_start against forecasted_start"""
    if value >= instance.forecasted_start:
        raise ValueError(
            "Forecasted start datetime should be after forecast start datetime."
        )


def _validate_path(instance, attribute, value):
    """Check the path is a directory and creates it if it is not"""
    if not value.is_dir():
        value.mkdir()
        logger.info(f"Created directory at {value.absolute()}")


def _validate_raw_not_processed(instance, attribute, value):
    """Check that `raw_cache` and `processed_cache` are distinct."""
    if instance.processed_cache:
        if value.absolute() == instance.processed_cache.absolute():
            raise ValueError(
                f"{attribute.name} should be distinct from processed_cache"
            )


def _enumerate_tables(tables: List[str], table_str: str, range_to: int):
    """Given a table name, populates a list with enumerated table names

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


def _construct_sqlloader_filename(
    year: int, month: int, forecast_type: str, table: str
) -> str:
    """Constructs filename without file type

    Args:
        year: Year
        month: Month
        forecast_type: `P5MIN`, `PREDISPATCH`, `PDPASA`, `STPASA` or `MTPASA`
        table: The name of the table required
    Returns:
        Filename string without file type
    """
    (stryear, strmonth) = (str(year), str(month).rjust(2, "0"))
    if forecast_type == "PREDISPATCH" and table != "MNSPBIDTRK":
        prefix = f"PUBLIC_DVD_{forecast_type}{table}"
    else:
        prefix = f"PUBLIC_DVD_{forecast_type}_{table}"
    fn = prefix + f"_{stryear}{strmonth}010000"
    return fn


def generate_sqlloader_filenames(
    forecast_start: datetime,
    forecast_end: datetime,
    forecast_type: str,
    tables: List[str],
) -> Tuple[List[Tuple[int, int]], List[str]]:
    """Generates a list of MMSDM Historical Data SQLLoader file names based on query

    Args:
        forecast_start: Forecasts made at or after this datetime are queried.
        forecast_end: Forecasts made before or at this datetime are queried.
        forecast_type: `MTPASA`, `STPASA`, `PDPASA`, `PREDISPATCH` or `P5MIN`.
        tables: Table or tables required, provided as a List.
    Returns:
        A list of year-month tuples and corresponding format-agnostic
        (SQLLOader) filenames
    """
    intervening_dates = rrule.rrule(
        rrule.MONTHLY, dtstart=forecast_start, until=forecast_end
    )
    year_months = []
    fnames = []
    if "CONSTRAINTSOLUTION" in tables and forecast_type == "P5MIN":
        tables = _enumerate_tables(tables, "CONSTRAINTSOLUTION", 4)
    for table in tables:
        for date in intervening_dates:
            (year, month) = (date.year, date.month)
            fname = _construct_sqlloader_filename(year, month, forecast_type, table)
            fnames.append(fname)
            year_months.append((year, month))
    return year_months, fnames


@define
class Query:
    """`Query` validates user inputs and dispatches data fetchers.

    Construct `Query` using the `Query.initialise()` constructor. This
    ensures query metadata is constructed approriately.

    Query:

    - Validates user input data
        - Checks datetime are dd/mm/yyyy HH:MM
        - Checks datetime chronology (e.g. end is after start)
        - Validates `forecast_type`
        - *Validates user-supplied tables against what is available on NEMWeb*
    - Retains query metadata (via constructor class method `initialise`)
    - Can dispatch various Managers and Downloaders

    Attributes:
        forecast_start: Forecasts made at or after this datetime are queried.
        forecast_end: Forecasts made before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
        forecast_type: `MTPASA`, `STPASA`, `PDPASA`, `PREDISPATCH` or `P5MIN`.
        tables: Table or tables required. A single table can be supplied as
            a string. Multiple tables can be supplied as a list of strings.
        metadata: Metadata dictionary. Constructed by `Query.initialise()`.
        raw_cache (optional): Path to build or reuse raw cache.
        processed_cache (optional): Path to build or reuse processed cache. Should be
          distinct from raw_cache

    """

    forecast_start: datetime = field(
        converter=_dt_converter,
        validator=[_validate_forecast_chronology, _validate_relative_chronology],
    )
    forecast_end: datetime = field(converter=_dt_converter)
    forecasted_start: datetime = field(
        converter=_dt_converter, validator=[_validate_forecasted_chronology]
    )
    forecasted_end: datetime = field(converter=_dt_converter)
    forecast_type: str = field(
        validator=validators.in_(["MTPASA", "STPASA", "PDPASA", "PREDISPATCH", "P5MIN"])
    )
    tables: List[str] = field(converter=_tablestr_converter)
    metadata: Dict
    raw_cache: str = field(
        converter=Path,
        validator=[
            _validate_path,
            _validate_raw_not_processed,
        ],
    )
    processed_cache: Optional[str] = field(
        default=None,
        converter=converters.optional(Path),
        validator=validators.optional(_validate_path),
    )

    @classmethod
    def initialise(
        cls,
        forecast_start: str,
        forecast_end: str,
        forecasted_start: str,
        forecasted_end: str,
        forecast_type: str,
        tables: Union[str, List[str]],
        raw_cache: str,
        processed_cache: Optional[str] = None,
    ) -> "Query":
        """Constructor method for Query. Assembles query metatdata."""
        metadata = {
            "forecast_start": forecast_start,
            "forecast_end": forecast_end,
            "forecasted_start": forecasted_start,
            "forecasted_end": forecasted_end,
            "forecast_type": forecast_type,
            "tables": tables,
        }
        return cls(
            forecast_start=forecast_start,
            forecast_end=forecast_end,
            forecasted_start=forecasted_start,
            forecasted_end=forecasted_end,
            forecast_type=forecast_type,
            tables=tables,
            metadata=metadata,
            raw_cache=raw_cache,
            processed_cache=processed_cache,
        )

    def check_data_in_cache(self) -> bool:
        """Checks whether *all* requested data is already in the `raw_cache` as parquet

        `downloader` methods handle partial `raw_cache` completeness

        If all requested data is already in the `raw_cache` as parquet, returns True
        Otherwise returns False.
        """
        _, fnames = generate_sqlloader_filenames(
            self.forecast_start, self.forecast_end, self.forecast_type, self.tables
        )
        check = [
            (self.raw_cache / Path(fname + ".parquet")).exists() for fname in fnames
        ]
        if all(check):
            logging.info(f"Query raw data already downloaded to {self.raw_cache}")
            return True
        else:
            return False
