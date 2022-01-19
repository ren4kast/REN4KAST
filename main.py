from flask_ngrok import run_with_ngrok
from flask import Flask, make_response, request
from GeneralForecastHandler import get_forecasts_for_today, get_data_by_date
import pandas as pd
import numpy as np
from flask import jsonify

app = Flask(__name__)
# Defining the selected model params and method for each month.
available_exog_params = ['windspeed', 'GHI', 'temperature', 'X4']
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

run_with_ngrok(app)  # starts ngrok when the app is run

@app.route("/")
def home():
    return "<h1>Renewable Energy Generation Forecasting Service</h1><p>Please use api/v1/getForecasts or api/v2/getForecasts endpoints to get the forecasts.</p>"

@app.route("/api/v1/getForecasts", methods=["GET"])
def forecast():
    forecast = get_forecasts_for_today(monthly_config)
    resp = make_response(forecast.to_csv(columns=forecast.columns))
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp
    # return jsonify(forecast.values.tolist())

@app.route("/api/v2/getForecasts", methods=["GET"])
def forecast_v2():
    forecast, exog = get_forecasts_for_today(new_monthly_config)
    missing_columns = np.setdiff1d(available_exog_params, exog.columns.values.tolist())
    nan_df = pd.DataFrame(np.nan, index=forecast.index, columns=missing_columns.tolist())
    combined = pd.concat([forecast, exog, nan_df], axis=1, sort=False)

    #resp = make_response(forecast.to_csv(columns=forecast.columns))
    #resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    #resp.headers["Content-Type"] = "text/csv"
    return combined.to_json(orient='records')

@app.route("/api/v2/getData", methods=["GET"])
def get_data_35days():
    start = request.args.get('startDate')
    result = get_data_by_date(start)
    return result.to_json(orient='records')

def run_server():
    app.run()

def get_day_ahead_forecasts(config):
    return get_forecasts_for_today(config)