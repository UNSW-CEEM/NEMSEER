import ast
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pyarrow.parquet as pq  # type: ignore
import xarray as xr
from attrs import converters, define, field, validators
from dateutil.relativedelta import relativedelta

from .data import DATETIME_FORMAT, ENUMERATED_TABLES, FORECAST_TYPES

logger = logging.getLogger(__name__)


def _dt_converter(value: str) -> datetime:
    """Convert string to datetime.

    Args:
        value: String with format %Y/%m/%d %H:%M
    Returns:
        Datetime object
    Raises:
        ValueError: If provided datetime string is invalid
    """
    try:
        dt = datetime.strptime(value, DATETIME_FORMAT)
        return dt
    except ValueError:
        try:
            dt = datetime.strptime(value, DATETIME_FORMAT + ":%S")
            if dt.second != 0:
                raise ValueError("If seconds provided in datetime, must be zero.")
            else:
                return dt
        except ValueError:
            raise ValueError(
                "Datetime invalid."
                + " Datetime should be provided as yyyy/mm/dd HH:MM, "
                + " or yyyy/mm/dd HH:MM:00."
            )


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


def _validate_run_chronology(instance, attribute, value):
    """Validates run_start against run_end"""
    if value > instance.run_end:
        raise ValueError(
            "Forecast end datetime must be greater than or equal to"
            + " run start datetime."
        )


def _validate_forecasted_chronology(instance, attribute, value):
    """Validated forecasted_start against forecasted_end"""
    if value > instance.forecasted_end:
        raise ValueError(
            "Forecasted end datetime must be greater than or equal to"
            + " forecasted start datetime."
        )


def _validate_relative_chronology(instance, attribute, value) -> None:
    """Validates run_start against forecasted_start"""
    if value > instance.forecasted_start:
        raise ValueError(
            "Forecasted start datetime should be at or after run start datetime."
        )


def _validate_path(instance, attribute, value) -> None:
    """Check the path is a directory and creates it if it is not"""
    if not value.is_dir():
        value.mkdir()
        logger.info(f"Created directory at {value.absolute()}")


def _validate_raw_not_processed(instance, attribute, value) -> None:
    """Check that :attr:`raw_cache` and :attr:`processed_cache` are distinct."""
    if instance.processed_cache:
        if value.absolute() == instance.processed_cache.absolute():
            raise ValueError(
                f"{attribute.name} should be distinct from processed_cache"
            )


def _enumerate_tables(tables: List[str], table_str: str, range_to: int) -> List[str]:
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
        forecast_type: One of :data:`nemseer.forecast_types`. See :term:`forecast types`
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
    run_start: datetime,
    run_end: datetime,
    forecast_type: str,
    tables: List[str],
) -> Dict[Tuple[int, int, str], str]:
    """Generates MMSDM Historical Data SQLLoader file names based on provided query data

    Returns a tuple of query metadata (`table`, `year`, `month`) mapped to each filename

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecast_type: One of :data:`nemseer.forecast_types`.
        tables: Table or tables required, provided as a List.
    Returns:
        A tuple of query metadata (`table`, `year`, `month`) mapped to each
        format-agnostic (:term:`SQLLoader`) filename
    """

    def _determine_delta_months(start: datetime, end: datetime):
        """Determines the widest range of months that encompass :attr:`start` and
        :attr:`end.

        Edge cases must be appropriately handled:
            - 2014/05/31 and 2014/06/01 have relativedelta of 1 day, but two
              data months (05/2014 and 06/2014) are required.
            - 2014/05/31 23:00 to 2014/06/01 00:00 only require data for 05/2014

        Args:
            start: datetime of start
            end: datetime of end
        Returns
            delta_months, the total number of months to consider
        """
        MONTH = relativedelta(months=1)
        full_delta = relativedelta(end, start)
        delta_months = full_delta.months * MONTH
        if full_delta.years > 0:
            delta_months += full_delta.years * MONTH * 12
        if (
            (start + delta_months).month != end.month
            and not (end.day == 1 and end.hour == 0 and end.minute == 0)
            and (
                full_delta.days != 0 or full_delta.hours != 0 or full_delta.minutes != 0
            )
        ):
            delta_months += MONTH
        return delta_months.months + (delta_months.years * 12)

    MONTH = relativedelta(months=1)
    int_months = _determine_delta_months(run_start, run_end)
    intervening_dates = [run_start + x * MONTH for x in range(0, int_months + 1)]
    filename_data = {}
    for ftype in ENUMERATED_TABLES:
        if forecast_type == ftype:
            for table, enumerate_to in ENUMERATED_TABLES[ftype]:
                if table in tables:
                    tables = _enumerate_tables(tables, table, enumerate_to)
    for table in tables:
        for date in intervening_dates:
            (year, month) = (date.year, date.month)
            fname = _construct_sqlloader_filename(year, month, forecast_type, table)
            filename_data[(year, month, table)] = fname
    return filename_data


@define
class Query:
    """:class:`Query` validates user inputs and dispatches data downloaders and
    compilers

    Construct :class:`Query` using the :meth:`Query.initialise()` constructor. This
    ensures query metadata is constructed approriately.

    Query:

    - Validates user input data
        - Checks datetimes fit :attr:`yyyy/mm/dd HH:MM` format
        - Checks datetime chronology (e.g. end is after start)
        - Checks requested datetimes are valid for each :term:`forecast type`
        - Validates :term:`forecast type`
        - Validates user-requested tables against what is available on NEMWeb
    - Retains query metadata (via constructor class method
      :meth:`nemseer.query.Query.initialise`)
    - Can check :attr:`raw_cache` and :attr:`processed_cache` contents to streamline
      query compilation

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
        metadata: Metadata dictionary. Constructed by :meth:`Query.initialise()`.
        raw_cache: Path to build or reuse :term:`raw_cache`.
        processed_cache (optional): Path to build or reuse :term:`processed_cache`.
            Should be distinct from :attr:`raw_cache`
        processed_queries: Defaults to `None` on initialisation. Populated once
            :meth:`Query.find_table_queries_in_processed_cache` is called.

    """

    run_start: datetime = field(
        converter=_dt_converter,
        validator=[_validate_run_chronology, _validate_relative_chronology],
    )
    run_end: datetime = field(converter=_dt_converter)
    forecasted_start: datetime = field(
        converter=_dt_converter, validator=[_validate_forecasted_chronology]
    )
    forecasted_end: datetime = field(converter=_dt_converter)
    forecast_type: str = field(validator=validators.in_(FORECAST_TYPES))
    tables: List[str] = field(converter=_tablestr_converter)
    metadata: Dict[str, str]
    raw_cache: Path = field(
        converter=Path,
        validator=[
            _validate_path,
            _validate_raw_not_processed,
        ],
    )
    processed_cache: Optional[Path] = field(
        default=None,
        converter=converters.optional(Path),
        validator=validators.optional(_validate_path),
    )
    processed_queries: Union[Dict[str, Path], Dict] = field(default=None)

    @classmethod
    def initialise(
        cls,
        run_start: str,
        run_end: str,
        forecasted_start: str,
        forecasted_end: str,
        forecast_type: str,
        tables: Union[str, List[str]],
        raw_cache: str,
        processed_cache: Optional[str] = None,
    ) -> "Query":
        """Constructor method for :class:`Query`. Assembles query metatdata."""
        metadata = {
            "run_start": run_start,
            "run_end": run_end,
            "forecasted_start": forecasted_start,
            "forecasted_end": forecasted_end,
            "forecast_type": forecast_type,
        }
        return cls(
            run_start=run_start,  # type: ignore
            run_end=run_end,  # type: ignore
            forecasted_start=forecasted_start,  # type: ignore
            forecasted_end=forecasted_end,  # type: ignore
            forecast_type=forecast_type,  # type: ignore
            tables=tables,  # type: ignore
            metadata=metadata,  # type: ignore
            raw_cache=raw_cache,  # type: ignore
            processed_cache=processed_cache,  # type: ignore
        )

    def check_all_raw_data_in_cache(self) -> bool:
        """Checks whether *all* requested data is already in the :attr:`raw_cache` as
        parquet

        :meth:`nemseer.downloader.ForecastTypeDownloader.download_csv()`
        handles partial :attr:`raw_cache` completeness

        If all requested data is already in the :attr:`raw_cache` as parquet,
        returns True. Otherwise returns False.
        """
        fnames = generate_sqlloader_filenames(
            self.run_start, self.run_end, self.forecast_type, self.tables
        ).values()
        check = [
            (self.raw_cache / Path(fname + ".parquet")).exists() for fname in fnames
        ]
        if all(check):
            logging.info(f"Query raw data already downloaded to {self.raw_cache}")
            return True
        else:
            return False

    def find_table_queries_in_processed_cache(self, data_format: str) -> None:
        """Determines which tables already have queries saved in the
        :attr:`processed_cache`.

        If data_format=df, this function will sieve through the metadata of all parquet
        files in the :attr:`processed_cache`. Note that parquet metadata is UTF-8
        encoded. Similarly, data_format=xr will check the metadata of all netCDF files.

        Modifies :attr:`Query.processed_queries` from :class:`None` to a :class:`dict`.

        The :class:`dict` is empty if:

        1. :attr:`processed_cache` is :class:`None`
        2. No portion of the query has been saved in the :attr:`processed_cache`

        If a portion of the queries are saved in the :attr:`processed_cache`, then
        :attr:`Query.processed_queries` will be equal to a :class:`dict` that maps
        the saved query's table name to the saved query's filename.

        Args:
            data_format: As per :func:`nemseer.compile_data`
        """
        tables_in_pcache: Union[Dict[str, Path], Dict] = {}
        if not self.processed_cache:
            pass
        else:
            if data_format == "df":
                for file in self.processed_cache.glob("*.parquet"):
                    byte_metadata = pq.read_metadata(file).metadata
                    metadata = ast.literal_eval(
                        (byte_metadata["nemseer".encode()]).decode()
                    )
                    if (
                        metadata_table := metadata.pop("table")
                    ) in self.tables and metadata == self.metadata:
                        tables_in_pcache[metadata_table] = file
                    else:
                        continue
            elif data_format == "xr":
                for file in self.processed_cache.glob("*.nc"):
                    metadata = xr.open_dataset(file).attrs
                    if (
                        metadata_table := metadata.pop("table")
                    ) in self.tables and metadata == self.metadata:
                        tables_in_pcache[metadata_table] = file
                    else:
                        continue
            self.processed_queries = tables_in_pcache
