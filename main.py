from GeneralForecastHandler import get_forecasts_for_today

monthly_config = [
    [[(2, 0, 2), (2, 1, 1, 4), 'n'], "SARIMA", []],  # January
    [[(2, 0, 4), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # February
    [[(4, 0, 3), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # March
    [[(4, 1, 3), (2, 0, 2, 4), 'n'], "SARIMAX", ['windspeed', 'GHI']],  # April
    [[(4, 1, 4), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # May
    [[(4, 1, 3), (2, 0, 2, 4), 'n'], "SARIMA", []],  # June
    [[(4, 1, 4), (1, 0, 1, 4), 'n'], "SARIMAX", ['windspeed', 'GHI']],  # July
    [[(3, 1, 3), (2, 0, 2, 4), 'n'], "SARIMA", []],  # August
    [[(3, 1, 1), (2, 0, 2, 4), 'n'], "SARIMAX", ['windspeed', 'GHI']],  # September
    [[(4, 1, 3), (2, 0, 2, 4), 'n'], "SARIMA", []],  # October
    [[(3, 1, 3), (2, 0, 2, 4), 'n'], "SARIMA", []],  # November
    [[(3, 1, 4), (2, 0, 2, 4), 'n'], "SARIMA", []]  # December
]
new_monthly_config = [
    [[(4, 1, 2), (1, 0, 1, 4), 'n'], "SARIMAX", ['windspeed', 'temperature']],  # January
    [[(2, 0, 1), (1, 1, 2, 4), 'n'], "SARIMA", []],  # February
    [[(5, 1, 0), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # March
    [[(5, 1, 3), (2, 0, 2, 4), 'n'], "SARIMAX", ['windspeed', 'GHI']],  # April
    [[(2, 0, 1), (1, 1, 1, 4), 'n'], "SARIMAX", ['windspeed', 'GHI']],  # May
    [[(5, 0, 4), (2, 1, 2, 4), 'n'], "SARIMA", []],  # June
    [[(4, 1, 5), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # July
    [[(5, 1, 4), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # August
    [[(4, 1, 5), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'GHI']],  # September
    [[(4, 1, 1), (2, 0, 2, 4), 'n'], "SARIMA", []],  # October
    [[(5, 1, 1), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'temperature']],  # November
    [[(5, 1, 5), (0, 0, 0, 0), 'n'], "ARIMAX", ['windspeed', 'temperature']]  # December
]

def forecast_v1():
    return get_forecasts_for_today(monthly_config)

def forecast_v2(config=new_monthly_config):
    return get_forecasts_for_today(config)