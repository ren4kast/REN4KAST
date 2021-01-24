import json
import requests
import pandas as pd


# Getting historical weather data (wind speed) from meteostats
def get_weather_data(url, columns, start):
    response = requests.get(url)
    data = pd.json_normalize(json.loads(json.dumps(response.json()["data"])))
    data.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(data), freq='H')
    data.index.name = 'time'
    # replacing missing values with the previous non-missing value
    data[columns] = data[columns].ffill()
    return data


# Getting weather data for all cities (wind speed)
def bulk_get_weather_data(cities, station_ids, start, end, timezone):
    windspeed_data = []

    for i in range(len(cities)):
        # getting windspeed from meteostat
        windspeed_data.append(
            get_weather_data(
                "https://api.meteostat.net/v1/history/hourly?station={}&start={}&end={}&time_zone={}&time_format=Y-m-d%20H:i&key=OpDs5PvR".format(
                    station_ids[i], start, end, timezone), columns=["windspeed"], start=start))

    return windspeed_data
