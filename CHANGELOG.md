# Changelog

<!--next-version-placeholder-->
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
