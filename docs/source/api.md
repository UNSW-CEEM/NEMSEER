# API Reference

```{eval-rst}
.. currentmodule:: nemseer
```

## Classes

### Query

```{note}
Use the {meth}`initialise() <nemseer.query.Query.initialise()>` class method to create an instance of the {class}`Query <nemseer.query.Query>` object, as this method assembles metadata relevant to NEMSEER cache searching.
```

```{eval-rst}
.. autoclass:: nemseer.query.Query
   :members:
```

### Downloader

```{note}
Use the {meth}`from_Query() <nemseer.downloader.ForecastTypeDownloader.from_Query()>` class method to create an instance of the {class}`ForecastTypeLoader <nemseer.downloader.ForecastTypeDownloader>` object.
```

```{eval-rst}
.. autoclass:: nemseer.downloader.ForecastTypeDownloader
   :members:
```

### DataCompiler

```{note}
Use the {meth}`from_Query() <nemseer.data_compilers.DataCompiler.from_Query()>` class method to create an instance of the {class}`DataCompiler <nemseer.data_compilers.DataCompiler>` object.
```

```{eval-rst}
.. autoclass:: nemseer.data_compilers.DataCompiler
   :members:
```

## Functions

### Query handlers

```{eval-rst}
.. automodule:: nemseer.query
   :members: generate_sqlloader_filenames
```

### Scrapers and downloaders

**Scrapers**: These functions scrape the {term}`MMSDM Historical Data SQLLoader` repository to assist `nemseer` in validating inputs and providing feedback to users.

**Downloaders**: Used to download and unzip a `.zip` file.

```{eval-rst}
.. automodule:: nemseer.downloader
   :members: get_sqlloader_forecast_tables, get_sqlloader_years_and_months, get_unzipped_csv
```

### Data handlers

Functions for handling various data states.

Valid inputs for {func}`clean_forecast_csv <nemseer.data_handlers.clean_forecast_csv>` are the same as those for {func}`pandas.read_csv <pandas.read_csv()>`.

```{eval-rst}
.. automodule:: nemseer.data_handlers
   :members:
```

## Forecast-specific helpers

### Datetime validators

These validators are specific to each {term}`forecast type`. They are used prior to initiating data compilation, and check that user-supplied datetime inputs are valid for the relevant {term}`forecast type`.

```{eval-rst}
.. automodule:: nemseer.forecast_type.validators
   :members:
```

### Run time generators

Run time generators produce the widest valid {term}`run time` range for a particular {term}`forecast type` given {term}`forecasted_start` and {term}`forecasted_end`.

```{eval-rst}
.. automodule:: nemseer.forecast_type.run_time_generators
   :private-members: _generate_P5MIN_runtimes, _generate_PREDISPATCH_runtimes, _generate_PDPASA_runtimes, _generate_STPASA_runtimes, _generate_MTPASA_runtimes
```

## Data

```{eval-rst}
.. automodule:: nemseer.data
   :members:
```
