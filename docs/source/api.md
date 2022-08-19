# API Reference

```{eval-rst}
.. currentmodule:: nemseer
```

## Classes

### Query Class

```{note}
Use the {meth}`initialise() <nemseer.query.Query.initialise()>` class method to create an instance of the {class}`Query <nemseer.query.Query>` object, as this method assembles metadata relevant to NEMSEER cache searching.
```

```{eval-rst}
.. autoclass:: nemseer.query.Query
   :members:
```

### Downloader Class

```{note}
Use the {meth}`from_Query() <nemseer.downloader.ForecastTypeDownloader.from_Query()>` class method to create an instance of the {class}`ForecastTypeLoader <nemseer.downloader.ForecastTypeDownloader>` object.
```

```{eval-rst}
.. autoclass:: nemseer.downloader.ForecastTypeDownloader
   :members:
```

## Functions

### Scrapers and downloaders

**Scrapers**: These functions scrape NEMWeb to assist `nemseer` in validating inputs and providing feedback to users.

**Downloader**: The downloader function is used to download a `.zip` file.

```{eval-rst}
.. automodule:: nemseer.downloader
   :members:
```

### Data handlers

Functions for handling various data states.

Valid inputs for {func}`clean_forecast_csv <nemseer.data_handlers.clean_forecast_csv>` are the same as those for {func}`pandas.read_csv <pandas.read_csv()>`

```{eval-rst}
.. automodule:: nemseer.data_handlers
   :members:
```

## Forecast-specific validators

These validators are specific to each `forecast_type`. They are used prior to initiating any downloads or other query actions (i.e. via {class}`Query <nemseer.query.Query>`), and check the following:

- The requested table(s) is (are) available for the provided `forecast_start` and `forecast_end`
- `forecast` times are compatible with `forecasted` times. These will depend on the forecast windows of each `forecast_type`

```{eval-rst}
.. automodule:: nemseer.forecast_type_validators
   :members:
```
