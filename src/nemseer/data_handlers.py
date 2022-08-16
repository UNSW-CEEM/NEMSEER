import pandas as pd


def _construct_sqlloader_filename(
    year: int, month: int, forecast_type: str, table: str
) -> str:
    """ Constructs filename without file type

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


def _parse_datetime_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Finds datetime columns in the DataFrame and converts them to datetime

    Args:
        df: pandas.DataFrame()
    Returns:
        DataFrame with datetime columns converted according to standard AEMO format
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
        "OFFERDATE"
    }
    dt_cols_present = dt_cols.intersection(set(df.columns.tolist()))
    dt_format = "%Y/%m/%d %H:%M:%S"
    for col in dt_cols_present:
        df.loc[:, col] = pd.to_datetime(df[col], format=dt_format)
    return df


def _parse_id_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Finds relevant ID columns in the DataFrame and converts them to cateogries

    Args:
        df: pandas.DataFrame()
    Returns:
        DataFrame with ID columns converted to categories
    """
    id_cols = {
        "CONSTRAINTID",
        "INTERCONNECTORID",
        "DUID",
        "CONNECTIONPOINTID",
        "PARTICIPANTID",
        "EXPORTGENCONID",
        "IMPORTGENCONID",
        "REGIONID"
    }
    id_cols_present = id_cols.intersection(set(df.columns.tolist()))
    for col in id_cols_present:
        df.loc[:, col] = df[col].astype('category')
    return df


def clean_forecast_csv(filepath_or_buffer: str) -> pd.DataFrame:
    """Given a forecast csv filepath or buffer, reads and cleans the forecast csv.

    Cleans artefacts in the forecast csv files.

    Args:
        filepath_or_buffer: As for pandas.read_csv()
    Returns:
        Cleaned DataFrame
    """
    # skip AEMO metadata
    df = pd.read_csv(filepath_or_buffer, skiprows=1, low_memory=False)
    # remove end of report line
    df = df.iloc[0:-1, :]
    drop_cols = df.columns.tolist()[0:4]
    df = df.drop(drop_cols, axis="columns")
    df = _parse_datetime_cols(df)
    df = _parse_id_cols(df)
    return df
