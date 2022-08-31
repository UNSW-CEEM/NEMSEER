# Glossary

```{glossary}
`run_start`
   Forecasts with run times at or after this datetime are queried.

`run_end`
   Forecasts with run times before or at this datetime are queried.

`run time`
   The time at which a forecast is *nominally* run.

`forecasted_start`
   Forecasts pertaining to times at or after this datetime are retained.

`forecasted_end`
   Forecasts pertaining to times before or at this datetime are retained.

`forecast type`
`forecast types`
   The term used in `nemseer` to refer to AEMO's ahead processes (as outlined in {term}`pre-dispatch` and {term}`PASA`).

`actual run time`
   The actual time at which the forecast run is executed/published. This is often reported in the `LASTCHANGED` column.


`MTPASA`
`STPASA`
`PDPASA`
`PASA`
   Projected Assessment of System Adequacy. PASA processes are focused on assessing reliability/resource adequacy.
     - `PDPASA` is run with a similar frequency and horizon to (30-minute) {term}`pre-dispatch`, and `STPASA` is run every hour or two following the horizon covered by `PDPASA`. Both attempt to maximise generation reserves available to the system given forecasts for demand and variable renewable energy generation, a simplified set of forecasted network constraints and participant-submitted resource availabilities and energy constraints. Together, they assess reliability for the next 7 trading days[^1]. Along with {term}`pre-dispatch` processes, PASA processes are used to identify Lack of Reserve (LOR) conditions. In the event of projected supply scarcity (i.e. forecasted LOR2 or LOR3), AEMO will estimate a latest time to intervene. If AEMO deems the market response to be insufficient by this time, it can exercise the Reliability and Emergency Reserve Trader (RERT), issue directions or issue instructions (i.e. instruct network service providers to commence load shedding)[^2].
     - Using participant-submitted resource availabilities, forecasted network constraints and resource short-run marginal costs (SRMC), `MTPASA` outputs are reported for each day following aggregation of the results of a market simulation run at half-hourly resolution. These outputs consist of system reliability forecasts (i.e. reporting unserved energy from the Reliability Run and loss of load probability from the Loss of Load Probability Run) that extend out for the next 24 months. In the Reliability Run, forecast uncertainty is addressed by using a range of reference weather years (at least 8) and at least two percentiles (i.e. probabilities of exceedence) for demand traces. Furthermore, each of these trace combinations are run using at least 100 random forced outage patterns[^3]. In the Loss of Load Probability Run, traces for "abstract" days are constructed based on monthly high demand and low variable renewable energy generation conditions observed over the different reference weather years. The Loss of Load Probability Run is used to determine the days that have a higher risk of load shedding. If the expected annual unserved energy, averaged across simulations in the Reliability Run, exceeds the maximum level specified by the reliability standard, a Low Reserve Condition (LRC) is identified. In response to LRCs, AEMO can direct generators to reschedule outages or contract for longer notice RERT[^2].

`PD`
`PREDISPATCH`
`P5MIN`
`5-minute pre-dispatch`
`pre-dispatch`
   Pre-dispatch processes consists of (30-minute) pre-dispatch (`PREDISPATCH`) and 5-minute pre-dispatch (`P5MIN`). To add to any confusion, when people or documents refer to "pre-dispatch", they are often referring to `PREDISPATCH`. The use of submitted participant offers distinguishes pre-dispatch processes from PASA processes. These are used alongside forecasts for constraints, demand and variable renewable energy generation to forecast dispatch conditions and regional prices for energy and FCAS. Along with {term}`PDPASA` and {term}`STPASA, pre-dispatch processes are used to identify Lack of Reserve (LOR) conditions. If AEMO deems the market response to be insufficient by this time, it can exercise the Reliability and Emergency Reserve Trader (RERT), issue directions or issue instructions (i.e. instruct network service providers to commence load shedding)[^2].
   - `PREDISPATCH` forecasts are generated every half hour at half-hourly resolution until the end of the last {term}`trading day` for which bid band price submission has closed (this occurs at 1230 EST)[^4].
   - `P5MIN` is run for every dispatch interval for the next hour.
   - For both `P5MIN` and `PREDISPATCH`, the impact of demand forecast error on regional energy prices and interconnector flows are explored through a sensitivity analysis[^5]. Only sensitivites for `PREDISPATCH` are available via the {term}`MMSDM Historical Data SQLLOader`.

`market day`
`trading day`
   From 0400 (exclusive) to 0400 (inclusive) on the next day (i.e. `(0400 Day 1, 0400 Day 2]`).

`MMSDM Historical Data SQLLOader`
`SQLLoader`
   An [archive of historical market data](http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/) used by `nemseer` for historical forecast data queries. Data is organised by year and month. The month corresponds to the month in which the forecast was run (i.e. if the month lies between {term}`run_start` and {term}`run_end`).
   - Within each month, there exists a directory for most of the data queried by `nemseer` (`DATA`), including pre-dispatch data with the most recent forecast run, and directories for *"complete"* pre-dispatch and 5-minute pre-dispatch data (`PREDISP_ALL_DATA` and `P5MIN_ALL_DATA`, respectively).
     - For pre-dispatch, the complete directory contains data with all forecast runs pertaining to a particular time.
     - As the data in the complete `P5MIN` directory appears to be the same as that in `DATA`, `nemseer` does not use this directory.

`raw_cache`
   Directory to which `nemseer` downloads processed raw data. Processing by `nemseer` includes:
   - Removing file metadata from the start and end of the file
   - Parsing datetimes, including parsing `PREDISPATCHSEQNO` (in :term:`PREDISPATCH` tables) into a new datetime column
   - Caching raw data in a [parquet](https://www.databricks.com/glossary/what-is-parquet) format, which enables column-based queries and uses less disk space than CSV
   An invalid/corrupted files list (`.invalid_aemo_files.txt`) is also maintained in this directory if an invalid/corrupted zip is queried via `nemseer`. This prevents `nemseer` from downloading/compiling invalid/corrupted data from AEMO's database.
```

[^1]: Australian Energy Market Operator. Short Term PASA Process Description. Technical report,
March 2012; Australian Energy Market Commission. Updating Short Term PASA, Rule determination.
Technical report, May 2022.
[^2]: Australian Energy Market Operator, 2021. Short Term Reserve Management
[^3]: Australian Energy Market Operator, 2021. Medium Term PASA Process Description.
[^4]: Australian Energy Market Operator, 2021. Pre-dispatch operating procedure.
[^5]: Australian Energy Market Operator, 2021. Pre-Dispatch Sensitivities.
