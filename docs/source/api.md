# API Reference

```{eval-rst}
.. currentmodule:: nemseer
```

## Loader

```{note}
Use the {meth}`initialise() <nemseer.loader.Loader.initialise()>` class method to create an instance of the {class}`Loader <nemseer.loader.Loader>` object, as this method assembles metadata relevant to NEMSEER cache searching.
```

```{eval-rst}
.. autoclass:: nemseer.loader.Loader
   :members:
```

## Downloader

```{note}
Use the {meth}`from_Loader() <nemseer.downloader.ForecastTypeDownloader.from_Loader()>` class method to create an instance of the {class}`ForecastTypeLoader <nemseer.downloader.ForecastTypeDownloader>` object.
```

```{eval-rst}
.. autoclass:: nemseer.downloader.ForecastTypeDownloader
   :members:
```

### Downloader Helpers

#### Scrapers and downloaders

**Scrapers**: These functions scrape NEMWeb to assist `nemseer` in validating inputs and providing feedback to users.
**Downloader**: The downloader function is used to download a `.zip` file.

```{eval-rst}
.. automodule:: nemseer.dl_helpers.functions
   :members:
```

#### Data handlers

Functions for handling various data states.

Valid inputs for {func}`clean_forecast_csv <nemseer.data_handlers.clean_forecast_csv>` are the same as those for {func}`pandas.read_csv <pandas.read_csv()>`

```{eval-rst}
.. automodule:: nemseer.data_handlers
   :members:
```

#### Specific validators

These validators are specific to each `forecast_type`. They are used prior to initiating a download (i.e. via {class}`ForecastTypeDownloader <nemseer.downloader.ForecastTypeDownloader>`) and check the following:

- The requested table(s) is (are) available for the provided `forecast_start` and `forecast_end`
- `forecast` times are compatible with `forecasted` times. These will depend on the forecast windows of each `forecast_type`

```{eval-rst}
.. automodule:: nemseer.dl_helpers.validators
   :members:
```
