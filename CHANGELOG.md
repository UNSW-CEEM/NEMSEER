# Changelog

<!--next-version-placeholder-->

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
