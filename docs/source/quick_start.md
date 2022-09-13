# Quick start

```{testsetup}
from pathlib import Path
Path("./nemseer_cache/").mkdir()
Path("./processed_cache/").mkdir()
```

```{testcleanup}
for file in Path("./nemseer_cache/").iterdir():
    Path(file).unlink()
for file in Path("./processed_cache/").iterdir():
    Path(file).unlink()
Path("./nemseer_cache/").rmdir()
Path("./processed_cache/").rmdir()
```

`nemseer` lets you download raw historical forecast data from the {term}`MMSDM Historical Data SQLLoader`, cache it in the [parquet](quick_start:parquet) format and use `nemseer` to assemble and filter forecast data into a {class}`pandas.DataFrame` or {class}`xarray.Dataset` for further analysis. Assembled queries can optionally be saved to a [processed cache](<quick_start:processed cache>).

## Core concepts and information for users

### Glossary

Refer to the [glossary](glossary.md) for an overview of key terminology used in `nemseer`. This includes descriptions of datetimes accepted as inputs in `nemseer`:

- {term}`run_start`
- {term}`run_end`
- {term}`forecasted_start`
- {term}`forecasted_end`

```{note}
AEMO ahead process tables with forecasted results typically have *three* datetime columns:

1. A {term}`forecasted time` which the forecast outputs pertain to
2. A nominal {term}`run time`. For most forecast types, this is reported in the `RUN_DATETIME` column.
3. An {term}`actual run time`
   - The *actual* run time can differ from the *nominal* time. For example:
     - The 18:15 `P5MIN` run (`RUN_DATETIME`) may actually be run/published at 18:10 (`LASTCHANGED`)
     - The 18:30 `PREDISPATCH` run (`PREDISPATCHSEQNO`, which is parsed into `PREDISPATCH_RUN_DATETIME` by `nemseer`) may actually be run/published at 18:02 (`LASTCHANGED`)
```

The glossary also provides an overview of the various ahead processes run by AEMO, including:

- {term}`P5MIN`
- {term}`PREDISPATCH`
- {term}`PDPASA`
- {term}`STPASA`
- {term}`MTPASA`

### Parquet

[Parquet](https://www.databricks.com/glossary/what-is-parquet) files can be loaded using data analysis packages such as [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html), and work well with packages for handling large on-memory/cluster datasets (e.g. [dask](https://docs.dask.org/en/stable/generated/dask.dataframe.read_parquet.html)). Parquet offers efficient data compression and columnar data storage, which can mean faster queries from file. Parquet files also store file metadata (which can include table schema).

### Types of compiled data

`nemseer` has functionality that allows a user to compile data into two types of in-memory data structures:

- [pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html#dataframe). Pandas is a widely-used Python package for manipulating data.
- Multi-dimensional [xarray Datasets](https://docs.xarray.dev/en/stable/user-guide/data-structures.html#dataset). xarray is intended for handling and querying data across multiple dimensions (e.g. the regional price forecast for a particular {term}`forecasted time` from a range of {term}`run times`). For more information, refer to the [*Getting started*](https://docs.xarray.dev/en/stable/getting-started-guide/index.html) section of the xarray documentation. The [xarray tutorial](https://tutorial.xarray.dev/intro.html) is also an excellent resource. Converting to xarray can be [memory-intensive](<quick_start:managing memory>).

### Managing memory

Some queries via `nemseer` may require a large amount of memory to complete. While memory use is query-specific, we suggest that `nemseer` be used on a system with at least 8GB of RAM. 16GB+ is preferable.

However, there are some things you can try if you do run into issues with memory. The suggestions below also apply to large queries on powerful computers:

1. You can use `nemseer` to simply download raw data as CSVs or to then cache data in the parquet format. Once you have a cache, you can use tools like [dask](https://docs.dask.org/en/stable/index.html) to process chunks of data in parallel. You may be able to reduce peak memory usage this way. [Dask works best with data formats such as parquet](https://docs.dask.org/en/stable/best-practices.html#store-data-efficiently). It should be noted that `nemseer` converts a single AEMO CSV into a single parquet file. That is, it does not partition the parquet store.
2. Conversion to {class}`xarray.Dataset` can be memory intensive. As this usually occurs when the data to be converted has a high number of dimensions (as determined by `nemseer`), `nemseer` will print a warning prior to attempting to convert any such data. While [xarray integrates with dask](https://docs.xarray.dev/en/stable/user-guide/dask.html), this functionality is contingent on loading data from a netCDF file.

### Processed cache

The {term}`processed_cache` is optional, but may be useful for some users. Specifying a path for this argument will lead to `nemseer` saving queries (i.e. requested data filtered based on user-supplied {term}`run times` and {term}`forecasted times`) as [parquet](quick_start:parquet) (if the {class}`pandas.DataFrame` data structure is specified) or [netCDF](https://www.unidata.ucar.edu/software/netcdf/) (if the {class}`xarray.Dataset` data structure is specified).

If subsequent `nemseer` queries include this {term}`processed_cache`, `nemseer` will check file metadata of the relevant file types to see if a particular table query has already been saved. If it has, `nemseer` will compile data from the {term}`processed_cache`.

```{note}
Because `nemseer` looks at metadata stored *in* each file, it does not care about the file name as long as file extensions are preserved (i.e. `*.parquet`, `*.nc`). As such, files in the {term}`processed_cache` can be renamed from default file names assigned by `nemseer`.
```

```{warning}
Saving to netCDF will let you load xarray objects into memory. However, saving these datasets to netCDF files may take up large amounts of hard disk space.
```

### Deprecated tables

If tables have been deprecated, `nemseer` will print a warning when the table is being downloaded. Deprecated tables are documented {data}`here <nemseer.data.DEPRECATED_TABLES>`.

## What can I query?

`nemseer` has functionality to tell you what you can query. This includes valid [forecast types](<quick_start:forecast types>), [months and years](<quick_start:date range of available data>) for which data is available and requestable [tables](<quick_start:table availability>).

```{note}
While these functions allow you to explicitly query this information, it's worth noting that functions for [compiling data](<quick_start:compiling data>) and [downloading raw data ](<quick_start:downloading raw data>) validate inputs and provide feedback when invalid inputs (such as invalid forecast types or data date ranges) are supplied.
```

### Forecast types

You can access valid {term}`forecast types` with the command below.

```{doctest}
>>> import nemseer
>>> nemseer.forecast_types
('P5MIN', 'PREDISPATCH', 'PDPASA', 'STPASA', 'MTPASA')
```

### Date range of available data

The years and months available via AEMO's {term}`MMSDM Historical Data SQLLoader` can be queried as follows.

```{doctest}
>>> import nemseer
>>> nemseer.get_data_daterange()
{...}
```

### Table availability

You can also see which tables are available for a given year, month and {term}`forecast type`.

Below, we fetch {term}`pre-dispatch` tables available for January 2022 (i.e. this month would include or be between {term}`run_start` and {term}`run_end`):

```{doctest}
>>> import nemseer
>>> nemseer.get_tables(2022, 1, "PREDISPATCH")
['CASESOLUTION', 'CONSTRAINT', 'CONSTRAINT_D', 'INTERCONNECTORRES', 'INTERCONNECTORRES_D', 'INTERCONNECTR_SENS_D', 'LOAD', 'LOAD_D', 'MNSPBIDTRK', 'OFFERTRK', 'PRICE', 'PRICESENSITIVITIE_D', 'PRICE_D', 'REGIONSUM', 'REGIONSUM_D', 'SCENARIODEMAND', 'SCENARIODEMANDTRK']
```

AEMO's [MMS Data Model reports](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report.htm) describe tables and columns that are available via `nemseer`.

#### `PREDISPATCH` tables

```{note}
For some pre-dispatch table (`CONSTRAINT`, `LOAD`, `PRICE`, `INTERCONNECTORRES` and `REGIONSUM`), there are two types of tables. Those ending with `_D` only contain the latest forecast for a particular interval, whereas those without `_D` have all relevant forecasts for an interval of interest.
```

## Compiling data

The main use case of `nemseer` is to download raw data (if it is not available in the {term}`raw_cache`) and then compile it into a data format for further analysis/processing. To do this, `nemseer` has {func}`compile_data <nemseer.compile_data>`.

This function:

1. Downloads the relevant raw data and converts it into [parquet](quick_start:parquet) in the {term}`raw_cache`.
2. If it's supplied, interacts with a {term}`processed_cache` (see [below](<quick_start:compiling data to a processed cache>)).
3. Returns a dictionary consisting of compiled {class}`pandas.DataFrame`s or {class}`xarray.Dataset`s (i.e. assembled and filtered based on the supplied {term}`run times` and {term}`forecasted times`) mapped to their corresponding table name.

For example, we can compile {term}`STPASA` forecast data contained in the `CASESOLUTION` and `CONSTRAINTSOLUTION` tables. The query below will filter {term}`run times` between "2021/02/01 00:00" and "2021/02/28 00:00" and {term}`forecasted times` between 09:00 on March 1 and 12:00 on March 3. The returned {class}`dict` maps each of the requested tables to their corresponding assembled and filtered datasets. These datasets are {class}`pandas.DataFrame` as `data_format="df"` (this is the default for this argument).

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_data(
... run_start="2021/02/01 00:00",
... run_end="2021/02/28 00:00",
... forecasted_start="2021/03/01 09:00",
... forecasted_end="2021/03/01 12:00",
... forecast_type="STPASA",
... tables=["CASESOLUTION", "CONSTRAINTSOLUTION"],
... raw_cache="./nemseer_cache/",
... data_format="df",
... )
INFO: Downloading and unzipping CASESOLUTION for 2/2021
INFO: Downloading and unzipping CONSTRAINTSOLUTION for 2/2021
INFO: Converting PUBLIC_DVD_STPASA_CASESOLUTION_202102010000.CSV to parquet
INFO: Converting PUBLIC_DVD_STPASA_CONSTRAINTSOLUTION_202102010000.CSV to parquet
>>> data.keys()
dict_keys(['CASESOLUTION', 'CONSTRAINTSOLUTION'])
```

In the example above we include argument names, but these can be omitted.

You can also just query a single table, such as the query below:

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_data(
... "2021/02/01 00:00",
... "2021/02/28 00:00",
... "2021/03/01 09:00",
... "2021/03/01 12:00",
... "STPASA",
... "REGIONSOLUTION",
... "./nemseer_cache/",
... )
INFO: Downloading and unzipping REGIONSOLUTION for 2/2021
INFO: Converting PUBLIC_DVD_STPASA_REGIONSOLUTION_202102010000.CSV to parquet
>>> data.keys()
dict_keys(['REGIONSOLUTION'])
```

We can also compile data to an {class}`xarray.Dataset`. To do this, we need to set `data_format="xr"`:

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_data(
... "2021/02/01 00:00",
... "2021/02/28 00:00",
... "2021/02/28 00:30",
... "2021/02/28 00:55",
... "P5MIN",
... "REGIONSOLUTION",
... "./nemseer_cache/",
... data_format="xr",
... )
INFO: Downloading and unzipping REGIONSOLUTION for 2/2021
INFO: Converting PUBLIC_DVD_P5MIN_REGIONSOLUTION_202102010000.CSV to parquet
INFO: Converting REGIONSOLUTION data to xarray.
>>> data.keys()
dict_keys(['REGIONSOLUTION'])
>>> type(data['REGIONSOLUTION'])
<class 'xarray.core.dataset.Dataset'>
```

### Compiling data to a processed cache

As outlined [above](<quick_start:processed cache>), compiled data can be saved to the {term}`processed_cache` as parquet (if `data_format` = "df") or as netCDF files (if `data_format` = "xr").

If the same {term}`processed_cache` is supplied to subsequent queries, `nemseer` will check whether any portion of the subsequent query has already been saved in the {term}`processed_cache`. If it has, `nemseer` will load data from the {term}`processed_cache`, thereby bypassing any download/raw data compilation.

With a supplied {term}`processed_cache`, we can save the query to parquet (`data_format` = "df") or to netCDF (`data_format` = "xr"):

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_data(
... "2021/02/01 00:00",
... "2021/02/28 00:00",
... "2021/03/01 09:00",
... "2021/03/01 12:00",
... "STPASA",
... "REGIONSOLUTION",
... "./nemseer_cache/",
... processed_cache="./processed_cache/",
... )
INFO: Query raw data already downloaded to nemseer_cache
INFO: Writing REGIONSOLUTION to the processed cache as parquet
```

And if this saved query is a portion of another subsequent query, `nemseer` will load data from the {term}`processed_cache`:

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_data(
... "2021/02/01 00:00",
... "2021/02/28 00:00",
... "2021/03/01 09:00",
... "2021/03/01 12:00",
... "STPASA",
... ["CASESOLUTION", "REGIONSOLUTION"],
... "./nemseer_cache/",
... processed_cache="./processed_cache/",
... )
INFO: Query raw data already downloaded to nemseer_cache
INFO: Compiling REGIONSOLUTION data from the processed cache
INFO: Writing CASESOLUTION to the processed cache as parquet
```

### Validation and feedback

{func}`compile_data <nemseer.compile_data>` will validate user inputs and provide feedback on valid inputs. Specifically, it validates:

1. Basic datetime chronologies (e.g. {term}`run_end` not before {term}`run_start`)
2. Whether the requested {term}`forecast type` and table type(s) are valid
3. Whether the requested {term}`run times` and `forecasted times` are valid for the requested {term}`forecast type`. In other words, forecasts that are run between {term}`run_start` and {term}`run_end` only produce data for a certain range of {term}`forecasted times`. This varies between {term}`forecast types`. For more information, refer to the forecast-specific datetime {mod}`validators<nemseer.forecast_type.validators>`.

### Getting valid run times for a set of forecasted times

If you're interested in forecast data for a particular datetime range (i.e. between {term}`forecasted_start` and {term}`forecasted_end`) but not sure what the valid {term}`run times` for this range are, you can use {func}`generate_runtimes <nemseer.generate_runtimes>`.

This function returns the first {term}`run_start` and last {term}`run_end` between which forecast outputs for the {term}`forecasted times` are available.

In the example below, we request {term}`run times` that contain data for the {term}`forecasted times` used in the [compiling data examples](<quick_start:compiling data>):

```{doctest}
>>> import nemseer
>>> nemseer.generate_runtimes("2021/03/01 09:00", "2021/03/01 12:00", "STPASA")
('2021/02/22 14:00', '2021/02/28 14:00')
```

You can see that in the [compiling data examples](<quick_start:compiling data>) we had a wider {term}`run time` range. This is fine since filtering will only retain {term}`run times` that contain the requested {term}`forecasted times`. The inverse is not true: {func}`compile_data <nemseer.compile_data>` will raise errors if the requested {term}`forecasted times` are not valid/do not have forecast outputs for the requested {term}`run times`.

## Downloading raw data

You can download data to a cache using {func}`download_raw_data() <nemseer.download_raw_data>`. This function only downloads data to the {term}`raw_cache`.

CSVs can be retained by specifying `keep_csv=True`.

Unlike [compiling data](<quick_start:compiling data>), only one set of datetimes needs to be provided (though these datetimes are keyword arguments for this function):

1. Provide `forecasted_start` and `forecasted_end` only. `nemseer` will determine the appropriate `run_start` and `run_end` for this forecasted range (via {func}`nemseer.generate_runtimes`) and download the corresponding raw data.
2. Provide `run_start` and `run_end` only. Dummy forecasted times are used.

```{doctest}
>>> import nemseer
>>> nemseer.download_raw_data(
... forecast_type="P5MIN",
... tables="REGIONSOLUTION",
... raw_cache="./nemseer_cache/",
... forecasted_start="2020/01/02 00:00",
... forecasted_end="2020/01/02 00:30",
... keep_csv=False
... )
INFO: Downloading and unzipping REGIONSOLUTION for 1/2020
INFO: Converting PUBLIC_DVD_P5MIN_REGIONSOLUTION_202001010000.CSV to parquet
```

Alternatively, provide {term}`run times`:

```{doctest}
>>> import nemseer
>>> nemseer.download_raw_data(
... forecast_type="P5MIN",
... tables="REGIONSOLUTION",
... raw_cache="./nemseer_cache/",
... run_start="2021/01/02 00:00",
... run_end="2021/01/02 00:30",
... keep_csv=False
... )
INFO: Downloading and unzipping REGIONSOLUTION for 1/2021
INFO: Converting PUBLIC_DVD_P5MIN_REGIONSOLUTION_202101010000.CSV to parquet
```
