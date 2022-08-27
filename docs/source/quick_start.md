# Quick start

As of v0.2.0, you can download raw historical forecast data from the {term}`MMSDM Historical Data SQLLoader` via `nemseer` and cache it in the [parquet](https://www.databricks.com/glossary/what-is-parquet) format.

Parquet files can then be loaded using Python packages such as [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html) and [dask](https://docs.dask.org/en/stable/generated/dask.dataframe.read_parquet.html). Future `nemseer` functionality will focus on building out basic data handling capabilities (e.g. datetime filtering based on datetime inputs).

## Glossary

Refer to the [glossary](glossary.md) for an overview of key terminology. This includes descriptions of datetimes accepted as inputs in `nemseer`:

- {term}`run_start`
- {term}`run_end`
- {term}`forecasted_start`
- {term}`forecasted_end`

```{note}
AEMO ahead process tables with forecasted results typically have *three* datetime columns:

1. A `forecasted` time which the forecast outputs pertain to
2. A nominal {term}`run time`. For most forecast types, this is reported in the `RUN_DATETIME` column.
   - `P5MIN`: Every 5 minutes beginning on the hour
   - `PREDISPATCH/PDPASA`: Every 30 minutes beginning on the hour
   - `STPASA`: On the hour, either every hour or every two hours
     - Frequency of runs was increased in 2021
   - `MTPASA`: Run every week on Tuesdays, datetime of run will vary
3. An {term}`actual run time`
   - The *actual* `run` time can differ from the *nominal* time. For example:
     - The 18:15 `P5MIN` run (`RUN_DATETIME`) may actually be run/published at 18:10 (`LASTCHANGED`)
     - The 18:30 `PREDISPATCH` run (`PREDISPATCHSEQNO`, which is parsed into `PREDISPATCH_RUN_DATETIME` by `nemseer`) may actually be run/published at 18:02 (`LASTCHANGED`)
```

## Downloading raw data

You can download data to a cache using {func}`download_raw_data() <nemseer.download_raw_data>`. Note that `forecasted` times need to be provided but are not used.

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
... run_start="2020/01/01 00:00",
... run_end="2020/01/01 00:00",
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

{func}`download_raw_data() <nemseer.download_raw_data>` provides feedback on whether dates and the forecast type are valid. It will also let you know which tables are available if you enter an invalid table.

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

Below, we fetch pre-dispatch tables available for January, 2022 (i.e. this month would include or be between `run_start` and `run_end`):

```{doctest}
>>> import nemseer
>>> nemseer.get_tables(2022, 1, "PREDISPATCH")
['CASESOLUTION', 'CONSTRAINT', 'CONSTRAINT_D', 'INTERCONNECTORRES', 'INTERCONNECTORRES_D', 'INTERCONNECTR_SENS_D', 'LOAD', 'LOAD_D', 'MNSPBIDTRK', 'OFFERTRK', 'PRICE', 'PRICESENSITIVITIE_D', 'PRICE_D', 'REGIONSUM', 'REGIONSUM_D', 'SCENARIODEMAND', 'SCENARIODEMANDTRK']
```

##### `PREDISPATCH` tables

```{note}
For some pre-dispatch table (`CONSTRAINT`, `LOAD`, `PRICE`, `INTERCONNECTORRES` and `REGIONSUM`), there are two types of tables. Those ending with `_D` only contain the latest forecast for a particular interval, whereas those without `_D` have all relevant forecasts for an interval of interest.
```
