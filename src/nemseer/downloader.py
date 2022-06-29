from attrs import define
from nemosis import downloader

# Linux Chrome User-Agent header
USR_AGENT_HEADER = {
    'User-Agent': ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                   + "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
                   }

# Wholesale electricity data archive base URL
MMSDM_ARCHIVE_URL = "http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM"
