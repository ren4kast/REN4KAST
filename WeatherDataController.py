import json
import requests
import pandas as pd
import datetime
import time

# Getting historical weather data (wind speed) from meteostats
def get_weather_data(station_id, columns, start, end, timezone):
    url = "https://meteostat.p.rapidapi.com/stations/hourly"
    headers = {
        'x-rapidapi-host': "meteostat.p.rapidapi.com",
        'x-rapidapi-key': "ebc6c461c8msha94c704506eaebdp19f500jsn2935c012c6d7"
    }
    splitted_dates = split_dates(datetime.datetime.strptime(start, '%Y-%m-%d'), datetime.datetime.strptime(end, '%Y-%m-%d'))
    # getting first 29 days
    querystring = {"station": station_id, "start": splitted_dates[0][0], "end": splitted_dates[0][1], "tz": timezone}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data1 = pd.json_normalize(json.loads(json.dumps(response.json()["data"])))
    data1.index = pd.date_range(start="{} 00:00:00".format(splitted_dates[0][0]), periods=len(data1), freq='H')
    data1.index.name = 'time'
    # sleep due to api constraints
    time.sleep(0.3)
    # getting the next days
    querystring = {"station": station_id, "start": splitted_dates[1][0], "end": splitted_dates[1][1], "tz": timezone}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data2 = pd.json_normalize(json.loads(json.dumps(response.json()["data"])))
    data2.index = pd.date_range(start="{} 00:00:00".format(splitted_dates[1][0]), periods=len(data2), freq='H')
    data2.index.name = 'time'
    # replacing missing values with the previous non-missing value
    data2[columns] = data2[columns].ffill()
    # sleep due to api constraints
    time.sleep(0.3)
    # concatenating data
    data = pd.concat([data1, data2])
    return data

# Getting weather data for all cities (wind speed)
def bulk_get_weather_data(cities, station_ids, start, end, timezone):
    windspeed_data = []
    for i in range(len(cities)):
        # getting windspeed from meteostat
        windspeed_data.append(
            get_weather_data(station_ids[i], ["wspd"], start, end, timezone))
    return windspeed_data

def split_dates(start, end):
    interval = datetime.timedelta(days=29)
    periods = []
    period_start = start
    while period_start < end:
        period_end = min(period_start + interval, end)
        periods.append((period_start.strftime('%Y-%m-%d'), period_end.strftime('%Y-%m-%d')))
        period_start = period_end + datetime.timedelta(days=1)
    return periods