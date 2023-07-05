# Changelog

## v1.0.5 (5/05/2023)

- Support Python 3.11 and add to CI testing
- Update dependencies
- Relicense `nemseer` under GPL3 and documentation under CC BY

## v1.0.4 (5/12/2022)

- Version bump for Zenodo DOI

## v1.0.3 (9/11/2022)

- Fix `attrs` dependency version

## v1.0.2 (14/10/2022)

Minor fixes:

- Fix logging to use `nemseer` logger, not root logger
- Suppress pandas Future Warning

## v1.0.1 (27/09/2022)

- Where they exist, drop intervention periods when converting to xarray and provide user with warning

## v1.0.0 (26/09/2022)

- Links to examples in all functions in Core Functionality of documentation
- Detailed example of P5MIN demand forecast errors for 2021

## v0.7.1 (20/09/2022)

- Various bug fixes from beta testing
  - Selective conversion of CSV to parquet
  - Correctly implement intervening date generation for filename generation
- Example tidied up
- Seconds can now be supplied in datetime inputs (as long as they are `00`)

## v0.7.0 (08/09/2022)

- Implement `processed_cache
- Update documentation

## v0.6.0 (06/09/2022)

### Major features

- Compile data to xarray Dataset
- Smarter `download_raw_data` function

### Minor additions

- Additional downcasting in conversion to parquet to reduce memory/file size
- Update glossary with PD/STPASA run types
- Additional info in quick start

### Fixes

- Fix bug where data was mapped to enumerated table name
- Remove duplicate rows when compiling

## v0.5.0 (01/09/2022)

- Implement data compilation to pandas DataFrame
  - Add forecast-specific datetime validation to DataCompiler
  - Handle invalid/corrupted files during compilation
- Add runtime generators
- Expand testing for new functionality
- Move constants to data module
- Expand glossary and update README, API and quick start pages in docs

## v0.4.0 (27/08/2022)

- Improve docs, including addition of glossary
- Implement invalid/corrupt file handler for raw data downloading

## v0.3.2 (25/08/2022)

- Expand testing, including testing all to check zip content exits for all possible URLs
- Add hidden file handler for corrupted CSV/zips from NEMWeb
- Improve doc referencing
- Rename `forecast_start/end` to `run_start/end`
- Add forecast-type datetime validation and corresponding testing

## v0.3.1 (22/08/2022)

- Patch for functionality in v0.3.0
- Refactor `downloader` to reduce redundant code

## v0.3.0 (19/08/2022)

- Handle PREDISP_ALL_DATA (complete pre dispatch data for each month)
  - Associated testing
- Update to docs

## v0.2.1 (19/08/2022)

- Bug fix for Windows (PermissionError)
- Switch date format to `yyyy/mm/dd HH:MM` for consistency with NEMOSIS and AEMO date format
- Rename `Loader` to `Query`
- Lazy parquet conversion
- More testing, including doctesting of examples in Quick Start section of docs

## v0.2.0 (16/08/2022)

- More sophisticated handling of raw data in `raw_cache`:
  - Check whether query data exists in `raw_cache` prior to downloading data
  - Progress bar for downloads
  - Cache data as parquet, with select columns parsed as datetime or category
- Code base reorganised to facilitate function reuse

## v0.1.0 (28/07/2022)

- First release of `nemseer`!
  - User feedback regarding available tables
  - Basic user input validation
  - Download and unzip files based on query
