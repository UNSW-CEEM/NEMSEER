import logging
from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd

from .data import DATETIME_FORMAT, FORECASTED_COL, RUNTIME_COL

logger = logging.getLogger(__name__)


def _parse_datetime_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Finds datetime columns in the DataFrame and converts them to datetime

    Args:
        df: pandas.DataFrame
    Returns:
        :class:`pandas.DataFrame` with datetime columns converted according to standard
        AEMO
        format
    """
    dt_cols = {
        "DATETIME",
        "EFFECTIVEDATE",
        "INTERVAL_DATETIME",
        "RUN_DATETIME",
        "AUTHORISEDDATE",
        "LASTCHANGED",
        "VERSION_DATETIME",
        "DAY",
        "PUBLISH_DATETIME",
        "LATEST_OFFER_DATETIME",
        "STARTDATE",
        "ENDDATE",
        "PERIOD_ENDING",
        "GENCONID_EFFECTIVEDATE",
        "BIDSETTLEMENTDATE",
        "SETTLEMENTDATE",
        "OFFERDATE",
    }
    dt_cols_present = dt_cols.intersection(set(df.columns.tolist()))
    for col in dt_cols_present:
        df.loc[:, col] = pd.to_datetime(df[col], format=DATETIME_FORMAT)
    return df


def _parse_id_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Finds relevant ID columns in the DataFrame and converts them to categories

    Args:
        df: pandas.DataFrame
    Returns:
        :class:`pandas.DataFrame` with ID columns converted to categories
    """
    id_cols = {
        "CONSTRAINTID",
        "INTERCONNECTORID",
        "DUID",
        "CONNECTIONPOINTID",
        "PARTICIPANTID",
        "EXPORTGENCONID",
        "IMPORTGENCONID",
        "REGIONID",
    }
    id_cols_present = id_cols.intersection(set(df.columns.tolist()))
    for col in id_cols_present:
        df.loc[:, col] = df[col].astype("category")
    return df


def _parse_predispatch_seq_no(df: pd.DataFrame) -> pd.DataFrame:
    """Parses `PREDISPATCHSEQNO` as datetime and adds `PREDISPATCH_RUN_DATETIME`

    Args:
        df: pandas.DataFrame
    Returns:
        :class:`pandas.DataFrame` with additional column `PREDISPATCH_RUN_DATETIME`
    """
    df["PREDISPATCHSEQNO"] = df["PREDISPATCHSEQNO"].astype(int).astype(str)
    parsed = df["PREDISPATCHSEQNO"].str.extract(r"^([0-9]{8})([0-9]{2})$")
    year_month_day = pd.to_datetime(parsed[0], format="%Y%m%d")
    hour_min = ((parsed[1].astype(int) - 1) * pd.Timedelta(minutes=30)).add(
        pd.Timedelta(hours=4, minutes=30)
    )
    df["PREDISPATCH_RUN_DATETIME"] = year_month_day + hour_min  # type: ignore
    return df


def clean_forecast_csv(filepath_or_buffer: Union[str, Path]) -> pd.DataFrame:
    """Given a forecast csv filepath or buffer, reads and cleans the forecast csv.

    Cleans artefacts in the forecast csv files, including AEMO metadata at start of file
    and end of report line. Also removes any duplicate rows.

    Args:
        filepath_or_buffer: As for :func:`pandas.read_csv`
    Returns:
        Cleaned :class:`pandas.DataFrame` with forecast data
    Warning:
        Removes duplicate rows. Raises a warning when doing so.
    """
    # skip AEMO metadata
    df = pd.read_csv(filepath_or_buffer, skiprows=1, low_memory=False)
    # remove end of report line
    df = df.iloc[0:-1, :]
    drop_cols = df.columns.tolist()[0:4]
    df = df.drop(drop_cols, axis="columns")
    df = _parse_datetime_cols(df)
    df = _parse_id_cols(df)
    if "PREDISPATCHSEQNO" in df.columns:
        df = _parse_predispatch_seq_no(df)
    if any(dup_df := df.duplicated()):
        dup_rows = dup_df.loc[dup_df is True]
        logging.warning(
            "Duplicate rows detected. Dropping the following rows:\n" + f"{dup_rows}"
        )
        df = df.drop_duplicates()
    return df


def _filter_on_datetime_col(
    df: pd.DataFrame, dt_col: str, start: datetime, end: datetime
) -> pd.DataFrame:
    """Filter the given datetime column based on the supplied start and end times

    Args:
        df: pandas.DataFrame
        dt_col: Datetime columns in :attr:`df`
        start: Start datetime
        end: End datetime
    Returns
        DataFrame with datetime filtering applied on :attr:`dt_col`.
    """
    df = df.loc[df[dt_col] >= start, :]
    df = df.loc[df[dt_col] <= end, :]
    return df


def apply_run_and_forecasted_time_filters(
    df: pd.DataFrame,
    run_start: datetime,
    run_end: datetime,
    forecasted_start: datetime,
    forecasted_end: datetime,
    forecast_type: str,
) -> pd.DataFrame:
    """Applies filtering for run times (i.e. :term:`run_start` and :term:`run_end`) and
    forecasted times (i.e. :term:`forecasted_start` and :term:`forecasted_end`).

    Datetime filtering is applied to a column fetched from lookup tables that map
    the relevant column name to each :term:`forecast type`. If the run time/forecasted
    column obtained from the lookup is not present in the DataFrame, the respective
    filter is not applied.

    Args:
        run_start: Forecast runs at or after this datetime are queried.
        run_end: Forecast runs before or at this datetime are queried.
        forecasted_start: Forecasts pertaining to times at or after this
            datetime are retained.
        forecasted_end: Forecasts pertaining to times before or at this
            datetime are retaned.
        forecast_type: One of :data:`nemseer.forecast_types`.
    Returns:
        DataFrame with appropriate datetime filtering applied.
    """
    (runtime_col, forecasted_col) = (
        RUNTIME_COL[forecast_type],
        FORECASTED_COL[forecast_type],
    )
    for (start, end), col in zip(
        ((run_start, run_end), (forecasted_start, forecasted_end)),
        (runtime_col, forecasted_col),
    ):
        if col in df.columns:
            df = _filter_on_datetime_col(df, col, start, end)
    return df
