# nemseer
[![PyPI version](https://badge.fury.io/py/nemseer.svg)](https://badge.fury.io/py/nemseer)
[![Documentation Status](https://readthedocs.org/projects/nemseer/badge/?version=latest)](https://nemseer.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/UNSW-CEEM/NEMSEER/branch/master/graph/badge.svg?token=BO69YSQIGI)](https://codecov.io/gh/UNSW-CEEM/NEMSEER)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A package for downloading and handling forecasts for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO).

## Work in Progress

This package is a work in progress. For a high-level overview of development, check out the [roadmap](ROADMAP.md).

## Installation

```bash
pip install nemseer
```

## Usage

As of v0.2.0, you can download raw forecast data via `nemseer` and cache it in the [parquet](https://www.databricks.com/glossary/what-is-parquet) format. Parquet files can then be loaded using Python packages such as [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html) and [dask](https://docs.dask.org/en/stable/generated/dask.dataframe.read_parquet.html).

### Quick start

#### Forecast types

1. 5-minute pre-dispatch (`P5MIN`)
2. Pre-dispatch (`PREDISPATCH`)
3. Pre-dispatch Projected Assessment of System Adequacy (`PDPASA`)
4. Short Term Projected Assessment of System Adequacy (`STPASA`)
3. Medium Term Projected Assessment of System Adequacy (`MTPASA`)

#### Forecast dates

1. `forecast_start`: Forecasts made at or after this datetime are queried.
2. `forecast_end`: Forecasts made before or at this datetime are queried.
3. `forecasted_start`: Forecasts pertaining to times at or after this datetime are retained.
4. `forecasted_end`: Forecasts pertaining to times before or at this datetime are retained.

#### Downloading raw data

You can download data to a cache using `download_raw_data()`. Note that `forecasted` times need to be provided but are not used.

```python
import nemseer
nemseer.download_raw_data(
    forecast_start = "01/01/2020 00:00", 
    forecast_end = "02/01/2020 00:00",
    forecasted_start = "02/01/2020 00:00",
    forecasted_end = "02/01/2020 00:00",
    forecast_type = "P5MIN",
    tables = "REGIONSOLUTION",
    raw_cache = "/my/raw/cache/",
    keep_csv = False
)
```

or more simply:

```python
import nemseer
nemseer.download_raw_data(
    "01/01/2020 00:00", 
    "02/01/2020 00:00",
    "02/01/2020 00:00",
    "02/01/2020 00:00",
    "P5MIN",
    "REGIONSOLUTION",
    "/my/raw/cache/",
)
```

You can also query multiple tables for a given forecast type, and keep downloaded csvs:

```python
import nemseer
nemseer.download_raw_data(
    "01/01/2020 00:00", 
    "02/01/2020 00:00",
    "02/01/2020 00:00",
    "02/01/2020 00:00",
    "P5MIN",
    ["REGIONSOLUTION", "CASESOLUTION"],
    "/my/raw/cache/",
    keep_csv = True
)
```

Inputs are validated and suggestions are given where inputs are invalid (e.g. valid forecast types, valid tables).
### What else can I query?

`nemseer.download_raw_data()` provides feedback on whether dates and the forecast type are valid. It will also let you know which tables are available if you enter an invalid table.

If you want to query this information separately, you can use the calls below.

#### Forecast types

You can access valid forecast types with the command below.

```python
import nemseer
nemseer.forecast_types
```

#### Available forecast data

##### Data date range

The years and months available via AEMO's MMSDM Historical Data SQLLoader can be queried as follows.

```python
import nemseer
nemseer.get_data_daterange()
```
##### Table availability

You can also see which tables are available for a given year, month and forecast type. 

Below, we fetch STPASA tables available for January, 2022 (i.e. this month would include or be between `forecast_start` and `forecast_end`):
```python
import nemseer
nemseer.get_tables(2022, 1, "STPASA")
```

## Contributing

Interested in contributing? Check out the [contributing guidelines](CONTRIBUTING.md), which also includes steps to install `nemseer` for development.

Please note that this project is released with a [Code of Conduct](CONDUCT.md). By contributing to this project, you agree to abide by its terms.

## License

`nemseer` was created by Abhijith Prakash. It is licensed under the terms of the [BSD 3-Clause license](LICENSE).

## Credits

`nemseer` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

`nemseer` borrows functionality from [`NEMOSIS`](https://github.com/UNSW-CEEM/NEMOSIS), a package for extracting historical *actual* market data from AEMO's NemWeb.
