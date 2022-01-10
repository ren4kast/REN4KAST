from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
from GenerationDataController import calculate_renewables_percentage
from GeneralDataHandler import get_and_clean_historical_data

# Defining the selected model params and method for each month.
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


# training and getting the forecasts for SARIMAX and ARIMAX models
def run_and_save_S_ARIMAX_model(train, test_length, exog_train, exog_test, config):
    order, sorder, trend = config
    model = SARIMAX(train, order=order, seasonal_order=sorder, trend=trend, exog=exog_train)
    model_fit = model.fit()
    predict = model_fit.forecast(test_length, exog=exog_test)
    df = pd.DataFrame(predict, columns=['forecast'])
    df.index.name = "time"
    return df


# training and getting the forecasts for SARIMA models
def run_and_save_SARIMA_model(train, test_length, config):
    order, sorder, trend = config
    model = SARIMAX(train, order=order, seasonal_order=sorder, trend=trend)
    model_fit = model.fit()
    predict = model_fit.forecast(test_length)
    df = pd.DataFrame(predict, columns=['forecast'])
    df.index.name = "time"
    return df


# Auto selecting the best model for current month, gathering data and returning the model forecasts.
def get_forecasts_for_today():
    data_frequency_per_day = 96
    start = (datetime.today() - timedelta(days=35)).strftime('%Y-%m-%d')
    end = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_entsoe = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    timezone = "Etc/GMT"  # Europe/Berlin OR Etc/GMT
    # Getting renewables generation percentage from 35 days ago until the end of today
    renewables_percentage = calculate_renewables_percentage(
        pd.Timestamp(start, tz='Etc/GMT'), pd.Timestamp(end_entsoe, tz='Etc/GMT'),
        ((
             datetime.strptime(
                 end_entsoe,
                 '%Y-%m-%d') - datetime.strptime(
                 start,
                 '%Y-%m-%d')).days) * 96)

    # updating the type to float64
    renewables_percentage = renewables_percentage.apply(pd.to_numeric)

    # updating the index
    renewables_percentage.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(renewables_percentage),
                                                freq='15Min')

    config, model, exog_column_names = monthly_config[renewables_percentage.index[-1].month - 1]
    if model == "SARIMA":
        return run_and_save_SARIMA_model(renewables_percentage, data_frequency_per_day, config)
    else:  # SARIMAX or ARIMAX
        # Getting exogenous params (GHI, Wind speed) for ARIMAX and SARIMAX
        exog_params = get_and_clean_historical_data(start, end, timezone)[exog_column_names]
        # Updating the index and chaging type to float64
        exog_params.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(exog_params), freq='15Min')
        exog_params = exog_params.apply(pd.to_numeric)
        # training the model and returning the forecasts
        return run_and_save_S_ARIMAX_model(renewables_percentage, data_frequency_per_day,
                                           exog_params[:-data_frequency_per_day], exog_params[-data_frequency_per_day:],
                                           config)


# Auto selecting the best model for current month, gathering data and returning the model forecasts.
def get_monthly_approach_forecasts_for_today():
    data_frequency_per_day = 96
    start = (datetime.today() - timedelta(days=35)).strftime('%Y-%m-%d')
    end = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_entsoe = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    timezone = "Etc/GMT"  # Europe/Berlin OR Etc/GMT

    # Getting exogenous params (GHI, Wind speed) for ARIMAX and SARIMAX
    exog_params = get_and_clean_historical_data(start, end, timezone)
    # Updating the index and chaging type to float64
    exog_params.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(exog_params), freq='15Min')
    exog_params = exog_params.apply(pd.to_numeric)
    # training the model and returning the forecasts
    return exog_params
