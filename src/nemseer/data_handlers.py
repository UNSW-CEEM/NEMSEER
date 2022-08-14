import pandas as pd


def clean_forecast_csv(filepath_or_buffer: str):
    """Given a forecast csv filepath or buffer, reads and cleans the forecast csv.

    Cleans artefacts in the forecast csv files.

    Args:
        filepath_or_buffer: As for pandas.read_csv()
    Returns:
        Cleaned DataFrame
    """
    # skip AEMO metadata
    df = pd.read_csv(filepath_or_buffer, skiprows=1)
    # remove end of report line
    df = df.iloc[0:-1, :]
    drop_cols = df.columns.tolist()[0:4]
    df = df.drop(drop_cols, axis="columns")
    return df
