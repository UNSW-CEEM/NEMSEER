# Changelog

<!--next-version-placeholder-->

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
