# Quick Start

As of v0.2.0, you can download raw forecast data via `nemseer` and cache it in the [parquet](https://www.databricks.com/glossary/what-is-parquet) format. Parquet files can then be loaded using Python packages such as [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html) and [dask](https://docs.dask.org/en/stable/generated/dask.dataframe.read_parquet.html).

## Forecast dates

1. `forecast_start`: Forecasts made at or after this datetime are queried.
2. `forecast_end`: Forecasts made before or at this datetime are queried.
3. `forecasted_start`: Forecasts pertaining to times at or after this datetime are retained.
4. `forecasted_end`: Forecasts pertaining to times before or at this datetime are retained.

## Downloading raw data

You can download data to a cache using `download_raw_data()`. Note that `forecasted` times need to be provided but are not used.

```{testsetup}
from pathlib import Path
Path("./nemseer_cache/").mkdir()
```

```{testcleanup}
for file in Path("./nemseer_cache/").iterdir():
    Path(file).unlink()
Path("./nemseer_cache/").rmdir()
```

```{doctest}
>>> import nemseer
>>> nemseer.download_raw_data(
... forecast_start="2020/01/01 00:00",
... forecast_end="2020/01/01 00:00",
... forecasted_start="2020/01/02 00:00",
... forecasted_end="2020/01/02 00:00",
... forecast_type="P5MIN",
... tables="REGIONSOLUTION",
... raw_cache="./nemseer_cache/",
... keep_csv=False
... )
INFO: ...
INFO: ...
```

or more simply:

```{doctest}
>>> import nemseer
>>> nemseer.download_raw_data(
... "2020/01/01 00:00",
... "2020/01/02 00:00",
... "2020/01/02 00:00",
... "2020/01/02 00:00",
... "P5MIN",
... "REGIONSOLUTION",
... "./nemseer_cache/",
... )
INFO: ...
```

You can also query multiple tables for a given forecast type, and keep downloaded csvs:

```{doctest}
>>> import nemseer
>>> nemseer.download_raw_data(
... "2020/01/01 00:00",
... "2020/01/02 00:00",
... "2020/01/02 00:00",
... "2020/01/02 00:00",
... "P5MIN",
... ["REGIONSOLUTION", "CASESOLUTION"],
... "./nemseer_cache/",
... keep_csv = True
... )
INFO: ...
INFO: ...
INFO: ...
```

Inputs are validated and suggestions are given where inputs are invalid (e.g. valid forecast types, valid tables).

## What else can I query?

`nemseer.download_raw_data()` provides feedback on whether dates and the forecast type are valid. It will also let you know which tables are available if you enter an invalid table.

If you want to query this information separately, you can use the calls below.

### `nemseer` forecast types

You can access valid forecast types with the command below.

```{doctest}
>>> import nemseer
>>> nemseer.forecast_types
('P5MIN', 'PREDISPATCH', 'PDPASA', 'STPASA', 'MTPASA')
```

### Available forecast data

#### Data date range

The years and months available via AEMO's MMSDM Historical Data SQLLoader can be queried as follows.

```{doctest}
>>> import nemseer
>>> nemseer.get_data_daterange()
{...}
```

#### Table availability

You can also see which tables are available for a given year, month and forecast type.

Below, we fetch predispatch tables available for January, 2022 (i.e. this month would include or be between `forecast_start` and `forecast_end`):

```{doctest}
>>> import nemseer
>>> nemseer.get_tables(2022, 1, "PREDISPATCH")
['CASESOLUTION', 'CONSTRAINT', 'CONSTRAINT_D', 'INTERCONNECTORRES', 'INTERCONNECTORRES_D', 'INTERCONNECTR_SENS_D', 'LOAD', 'LOAD_D', 'MNSPBIDTRK', 'OFFERTRK', 'PRICE', 'PRICESENSITIVITIE_D', 'PRICE_D', 'REGIONSUM', 'REGIONSUM_D', 'SCENARIODEMAND', 'SCENARIODEMANDTRK']
```

Note that for some pre-dispatch table (`CONSTRAINT`, `LOAD`, `PRICE`, `INTERCONNECTORRES` and `REGIONSUM`), there are two types of tables. Those ending with `_D` only contain the latest forecast for a particular interval.
