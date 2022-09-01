# Quick start

```{testsetup}
from pathlib import Path
Path("./nemseer_cache/").mkdir()
```

```{testcleanup}
for file in Path("./nemseer_cache/").iterdir():
    Path(file).unlink()
Path("./nemseer_cache/").rmdir()
```

As of v0.5.0, you can download raw historical forecast data from the {term}`MMSDM Historical Data SQLLoader` via `nemseer`, cache it in the [parquet](quick_start:parquet) format and use `nemseer` to assemble and filter forecast data into {class}`pandas.DataFrame`s for further analysis.

## Future functionality

Future `nemseer` functionality will include:

- An option to assemble data into multi-dimensional [xarray](https://docs.xarray.dev/en/stable/getting-started-guide/quick-overview.html) {class}`Datasets <xarray.Dataset>`, which make querying across multiple dimensions (e.g. a range of {term}`run times` for a particular set of {term}`forecasted times`).
- An optional {term}`processed_cache`. If provided by the user, [netCDF](https://www.unidata.ucar.edu/software/netcdf/) files with query data will be saved in this cache.

## Brief intro to concepts

### Glossary

Refer to the [glossary](glossary.md) for an overview of key terminology. This includes descriptions of datetimes accepted as inputs in `nemseer`:

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

### Parquet

[Parquet](https://www.databricks.com/glossary/what-is-parquet) files can be loaded using data analysis packages such as [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html), and work well with packages for handling large on-memory/cluster datasets (e.g. [dask](https://docs.dask.org/en/stable/generated/dask.dataframe.read_parquet.html)). Parquet offers efficient data compression and columnar data storage, which can mean faster queries from file.

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

The main use case of `nemseer` is to download raw data (if it is not available) and then compile it into a data format for further analysis/processing. To do this, `nemseer` has {func}`compile_raw_data <nemseer.compile_raw_data>`.

This function:

1. Downloads the relevant raw data and converts it into [parquet](quick_start:parquet) in the {term}`raw_cache`
2. Returns a dictionary consisting of compiled {class}`pandas.DataFrame`s or {class}`xarray.Dataset`s (i.e. assembled and filtered based on the supplied {term}`run times` and {term}`forecasted times`) mapped to their corresponding table name.

```{attention}

Data compilation to {class}`xarray.Dataset` will be implemented in future releases.
```

For example, we can compile {term}`STPASA` forecast data contained in the `CASESOLUTION` and `CONSTRAINTSOLUTION` tables. The query below will filter {term}`run times` between "2021/02/01 00:00" and "2021/02/28 00:00" and {term}`forecasted times` between 09:00 on March 1 and 12:00 on March 3. The returned {class}`dict` maps each of the requested tables to their corresponding assembled and filtered datasets.

```{doctest}
>>> import nemseer
>>> data = nemseer.compile_raw_data(
... run_start="2021/02/01 00:00",
... run_end="2021/02/28 00:00",
... forecasted_start="2021/03/01 09:00",
... forecasted_end="2021/03/01 12:00",
... forecast_type="STPASA",
... tables=["CASESOLUTION", "CONSTRAINTSOLUTION"],
... raw_cache="./nemseer_cache/",
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
>>> data = nemseer.compile_raw_data(
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

### Validation and feedback

{func}`compile_raw_data <nemseer.compile_raw_data>` will validate user inputs and provide feedback on valid inputs. Specifically, it validates:

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

You can see that in the [compiling data examples](<quick_start:compiling data>) we had a wider {term}`run time` range. This is fine since filtering will only retain {term}`run times` that contain the requested {term}`forecasted times`. The inverse is not true: {func}`compile_raw_data <nemseer.compile_raw_data>` will raise errors if the requested {term}`forecasted times` are not valid/do not have forecast outputs for the requested {term}`run times`.

## Downloading raw data

You can download data to a cache using {func}`download_raw_data() <nemseer.download_raw_data>`. This function only downloads data to the {term}`raw_cache`.

CSVs can be retained by specifying `keep_csv=True`.

Like [compiling data](<quick_start:compiling data>), {term}`forecasted times` need to be provided. However, unlike data compilation, these times are not used and thus no forecast-specific validation is carried out.

```{note}
Further `nemseer` releases will streamline input provision for this function.
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
INFO: Downloading and unzipping REGIONSOLUTION for 1/2020
INFO: Converting PUBLIC_DVD_P5MIN_REGIONSOLUTION_202001010000.CSV to parquet
```
