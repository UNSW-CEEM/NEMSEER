#: Forecast types requestable through nemseer.
#: See also :term:`forecast types`, and :term:`pre-dispatch` and :term:`PASA`.
FORECAST_TYPES = ("P5MIN", "PREDISPATCH", "PDPASA", "STPASA", "MTPASA")

MMSDM_ARCHIVE_URL = "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/"
"""Wholesale electricity data archive base URL"""

#: Tables which should be directed to the PREDISP_ALL_DATA URL.
#: The corresponding tables in the DATA folder (which end with "_D") only contain the
#: latest forecasted value
PREDISP_ALL_DATA = ("CONSTRAINT", "INTERCONNECTORRES", "PRICE", "LOAD", "REGIONSUM")

MTPASA_DUID_URL = "http://nemweb.com.au/Reports/Current/MTPASA_DUIDAvailability/"
"""MTPASA DUID Availability"""

#: Enumerated tables for each forecast type
#: First element of tuple is table name
#: Second element of tuple is number which to enumerate table to
ENUMERATED_TABLES = {
    "P5MIN": [("CONSTRAINTSOLUTION", 4)],
    "PREDISPATCH": [("CONSTRAINT", 2), ("LOAD", 2)],
}

DEPRECATED_TABLES = {
    "MTPASA": [
        "CASESOLUTION",
    ],
}
"""
Deprecated tables
"""

DATETIME_FORMAT = "%Y/%m/%d %H:%M"
"""
`nemseer` date format
"""

RUNTIME_COL = {
    "P5MIN": "RUN_DATETIME",
    "PREDISPATCH": "PREDISPATCH_RUN_DATETIME",
    "PDPASA": "RUN_DATETIME",
    "STPASA": "RUN_DATETIME",
    "MTPASA": "RUN_DATETIME",
}
"""
If it exists, `nemseer` will use the corresponding column for `run` time filtering.
"""

FORECASTED_COL = {
    "P5MIN": "INTERVAL_DATETIME",
    "PREDISPATCH": "DATETIME",
    "PDPASA": "INTERVAL_DATETIME",
    "STPASA": "INTERVAL_DATETIME",
    "MTPASA": "DAY",
}
"""
If it exists, `nemseer` uses the corresponding column for `forecasted` time filtering.
"""

ID_COLS = {
    "STUDYREGIONID",
    "CONSTRAINTID",
    "INTERCONNECTORID",
    "DUID",
    "CONNECTIONPOINTID",
    "PARTICIPANTID",
    "EXPORTGENCONID",
    "IMPORTGENCONID",
    "REGIONID",
    "LINKID",
    "USE_ITERATION_ID",
    "RESERVELIMITID",
    "SCENARIO",
}

TYPE_COLS = {
    "BIDTYPE",
    "RUNTYPE",
    "RUN_NO",
    "DEMAND_POE_TYPE",
    "AGGREGATION_PERIOD",
    "PERIOD_ENDING",
    "EFFECTIVEDATE",
    "VERSION_DATETIME",
}

DATETIME_COLS = {
    "DATETIME",
    "EFFECTIVEDATE",
    "INTERVAL_DATETIME",
    "RUN_DATETIME",
    "AUTHORISEDDATE",
    "LASTCHANGED",
    "VERSION_DATETIME",
    "DAY",
    "PUBLISH_DATETIME",
    "LATEST_OFFER_DATETIME",
    "STARTDATE",
    "ENDDATE",
    "PERIOD_ENDING",
    "GENCONID_EFFECTIVEDATE",
    "BIDSETTLEMENTDATE",
    "SETTLEMENTDATE",
    "OFFERDATE",
}

INVALID_STUBS_FILE = ".invalid_aemo_files.txt"
"""File in :term:`raw_cache` that contains invalid/corrupted AEMO files"""

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36)"
    ),
    "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) "
        + "Gecko/20100101 Firefox/49.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/"
        + "11.1.2 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 "
        + "(KHTML, like Gecko) Version/9.1.2 Safari/601.7.7"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) "
        + "Gecko/20100101 Firefox/45.0"
    ),
    (
        "Mozilla/5.0 (X11; CrOS x86_64 14268.67.0) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36)"
    ),
    (
        "Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , "
        + "D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless))"
    ),
    "Wget/1.12 (linux-gnu)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64; U; en-us) AppleWebKit/537.36 (KHTML, "
        + "like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/E7FBAF)"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) "
        + "Qt/4.8.1 Safari/E7FBAF"
    ),
    (
        "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko)"
        + "Raspbian Chromium/74.0.3729.157 Chrome/74.0.3729.157 Safari/537.36"
    ),
]
