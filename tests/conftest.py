import pytest

from nemseer.downloader import get_sqlloader_years_and_months


@pytest.fixture(scope="module")
def get_test_year_and_month():
    years_months = get_sqlloader_years_and_months()
    test_index = int(len(years_months) / 2)
    test_year = list(years_months.keys())[test_index]
    test_month = years_months[test_year][5]
    return (test_year, test_month)


@pytest.fixture(scope="module")
def valid_datetimes():
    forecast_start = "2021/02/01 00:00"
    forecast_end = "2021/02/05 00:00"
    forecasted_start = "2021/02/08 00:00"
    forecasted_end = "2021/02/08 23:55"
    return forecast_start, forecast_end, forecasted_start, forecasted_end
