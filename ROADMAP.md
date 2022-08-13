# Development Roadmap

## Process Description

### User Groups and Functionality

Two types of functionality would be exposed:
1. User functions (NEMOSIS-style) that enable the user to go end-to-end quickly. This would 'automate' the chain from raw cache/download to validation to aggregation to processed cache.
2. Advanced interface/API. Really this is just exposing the classes to the user so they can do more with it if need be

### Automated workflow

1. Loader is initialised with user input
2. Then:
    a) Loader checks metadata of netCDF via`CompiledProcessedData`. If no such metadata exists, proceed to b).
    b) Loader loads from the raw cache (via `CompiledRawData`), or dispatches a `ForecastTypeDownloader`. RawCache will consist of partioned parquet files (corresponding to original CSVs). Generic as well as forecast-specific validators should verify user inputs. Returns `CompiledRawData`.

3. If 2(a), then passed to `AggregatedForecastbyType` for data aggregation, filtering and building to processed cache
4. If 2(b), could then be passed to `AggregatedForecastbyType` for specific filtering?

By step 3/4, the datasets should be useful  enough to answer questions such as:
>I want to look at forecast convergence for 1 day of delivery, for predispatch runs as time approaches the delivery time.

5. `CompiledProcessedData` is saved as netCDF or flattened to csv via pandas. Metadata inserted into netCDF.


## Extensions

1. A very useful thing would be to have functionality to patch in NEMOSIS and do forecasts vs actual (`ForecastActualHandler`)


## Class Diagram

```mermaid
classDiagram

    class Loader{
      +String forecast_type
      +datetime forecast_time_start
      +datetime forecast_time_end
      +datetime forecasted_time_start
      +datetime forecasted_time_end
      +List tables
      +String raw_cache
      +String raw_format
      +String processed_cache
      +Dict metadata
      +load_data()
      +assemble_metadata()
      +generic_input_validation(all inputs)
      +forecasttype_input_validation(forecast_type)
      +check_processed_cache()
      +load_from_raw_cache()
      +download_and_convert_data(all inputs)
    }

    class ForecastTypeDownloader{
      +datetime forecast_times
      +datetime forecasted_times
      +List tables
      +String raw_cache
      +@classmethod initialise(forecast_type)
      +url_constructor()
      +download_month_year_table()
      +table_to_dataframe()
      +list_available_yearmonths()
      +list_available_tables(forecast_type)
    }
    class ForecastTypeValidators{
      +forecast_times
      +forecasted_times
      +List tables
      -@classmethod create_ForecastTypeValidator()
      -validate_inputs_for_forecasttype()
    }
    class RawCacheManager{
      +datetime forecasted_times
      +datetime forecast_times
      +List tables
      +String raw_cache
      +String desired_cache_format
      +@classmethod create_RawCacheManager()
      +check_if_downloaded(all except desired_cache_format)
      +load_from_raw_cache(all except desired_cache_format)
      +write_to_raw_cache(all inputs)
      +delete_rawcache_data(set(cache_formats)-set(desired_cache_format))
    }

      class ProcessedCacheManager{
      +datetime forecasted_times
      +datetime forecast_times
      +List tables
      +String processed_cache
      +Dict metadata
      +@classmethod create_ProcessedCacheManager()
      +check_if_available(metadata)
      +netCDF_to_processed_cache(processed_cache)
      +flatten_to_processed_cache(processed_cache)
    }

    class AggregatedForecastbyType{
      +datetime forecasted_times
      +datetime forecast_times
      +String type
      +List tables
      +String processed_cache
      +None compiled_data
      +date_filtering()
      +col_filtering()
      +merging()
      +construct_metadata()
      +build_xarray()
      +compile_to_processed_cache()
      +@classmethod aggregate_forecasts()
    }

    class CompiledRawData{

    }
    class CompiledProcessedData{

    }

    Loader -- ForecastTypeValidators :initialised by forecasttype_input_validation()\nOne for each forecast type
    Loader -- RawCacheManager :initialised by load_from_rawcache()
    Loader -- ProcessedCacheManager :initialised by check_processed_cache()
    Loader -- ForecastTypeDownloader :initialised by download_and_convert_data()\nOne for each forecast_type
    AggregatedForecastbyType -- ProcessedCacheManager : initialised by compile_to_processed_cache()
    RawCacheManager -- CompiledRawData
    ForecastTypeDownloader --CompiledRawData
    CompiledRawData -- AggregatedForecastbyType
    AggregatedForecastbyType -- CompiledProcessedData
    ProcessedCacheManager -- CompiledProcessedData
    class CrossForecastTypeHandler

    class ForecastActualHandler
```
