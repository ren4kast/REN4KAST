import pandas as pd
from RadiationDataController import bulk_get_radiation_data
from WeatherDataController import bulk_get_weather_data
import requests
from datetime import datetime, timedelta
import json

# Merging gathered data from different cities by taking average
def merge_datasets_by_taking_average(df, target_columns):
    assert_on_number_of_rows(df)
    output = []
    for row in range(len(df[0])):
        output.append([])
        for col in target_columns:
            sum = 0
            for i in range(len(df)):
                sum = sum + float(df[i][col][row])
            mean = sum / (len(df))
            output[row].append(mean)
    return pd.DataFrame([x for x in output], columns=target_columns, index=df[0].index)


# Asserting that number of rows among different datasets are equal
# If it is not equal, then some datapoints are missing
def assert_on_number_of_rows(df):
    for i in df:
        assert len(i) == len(df[0]), "Number of rows did NOT match! {} vs. {}".format(len(df[0]), len(i))

def get_weather_stations():
    cities = ["memmingen", "Rostock Warnem-u00fcnde", "Osnabrueck", "Braunschweig", "Cuxhaven", "Luebeck", "Berlin",
              "Bonn", "Hof", "Freudenstadt", "München", "Meiningen"]
    station_ids = ["10947", "10170", "10315", "10348", "10131", "10156", "10382", "10513", "10685", "10815", "10865",
                   "10548"]
    latitude = ["47.9833", "54.1833", "52.1333", "52.3", "53.8667", "53.8167", "52.5667", "50.8667", "50.3167", "48.45",
                "48.1333", "50.5667"]
    longitude = ["10.2333", "12.0833", "7.7", "10.45", "8.7", "10.7", "13.3167", "7.1667", "11.8833", "8.4167", "11.55",
                 "10.3833"]
    altitude = ["634", "4", "48", "81", "5", "14", "37", "91", "565", "797", "520", "450"]
    return cities, station_ids, latitude, longitude, altitude

# Get weather data from meteostat for defined cities
def get_and_clean_historical_data(start, end, timezone):
    cities, station_ids, latitude, longitude, altitude = get_weather_stations()

    # Getting data for cities
    windspeed_data = bulk_get_weather_data(cities, station_ids, start, end, timezone)
    ghi_data = bulk_get_radiation_data(cities, start, end, latitude, longitude, altitude)

    # merging data from different cities by taking average
    average_meteoParams = merge_datasets_by_taking_average(windspeed_data, ["wspd", "temp"])
    average_ghi = merge_datasets_by_taking_average(ghi_data, ["GHI"])
    # upsampling windspeed data (since it is hourly)
    upsampled_data = average_meteoParams.resample('15min').mean()
    # filling the upsampled datapoints using interpolation
    filledData_spline = upsampled_data.interpolate(method='spline', order=2).round(3)

    # windspeed data is available until  23:00, so using last data point to make data until 23:45
    last_datapoint = filledData_spline.loc[[filledData_spline.index[-1]]]
    for i in range(3):
        filledData_spline = filledData_spline.append(last_datapoint, ignore_index=False)

    # for missing ghi (normally 1 day)
    # Use last data (from yesterday)
    average_ghi_fixed = average_ghi.copy()
    for i in range(len(filledData_spline) - len(average_ghi_fixed)):
       average_ghi = average_ghi.append(average_ghi_fixed.loc[[average_ghi_fixed.index[len(average_ghi_fixed) - len(filledData_spline) + i]]], ignore_index=False)

    assert_on_number_of_rows([average_ghi, filledData_spline])
    filledData_spline.index = average_ghi.index

    result = pd.concat([filledData_spline, average_ghi], axis=1, sort=False)
    result.columns = ["windspeed", "temperature", "GHI"]
    # appending the windspeed and GHI data (exogenous params) for today and tomorrow
    return result


# Getting exogenous params for today and tomorrow
def get_today_and_tomorrow_exog_data_request(latitude, longitude, start, end, columns):
    url = "https://weatherbit-v1-mashape.p.rapidapi.com/forecast/hourly"
    querystring = {"lat": latitude, "lon": longitude, "hours": "48"}

    headers = {
        'x-rapidapi-host': "weatherbit-v1-mashape.p.rapidapi.com",
        'x-rapidapi-key': "f00df48a34msha857b3f5bd76f9fp10a955jsn7455a5604803"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    jsondata = json.loads(response.text)
    df = pd.json_normalize(jsondata['data'])

    #TODO: data starts from now, should be called a few minutes before the day before the forecast (at around 23:58 for forcasting the day after tomorrow)
    # assert datetime.now().hour == 23, "The service is supposed to call after 23:00 to retrieve data for the day before forecast."
    df.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(df), freq='H')
    df.index.name = 'time'

    # replacing missing values with the previous non-missing value
    df[columns] = df[columns].ffill()

    # changing type from non-type to float. because later we want to calculate the average among all cities
    df[columns] = df[columns].apply(pd.to_numeric)

    # metric conversion: m/s to km/h ~ 3.6
    df['wind_spd'] = [element * 3.6 for element in df['wind_spd']]
    return df


# getting exogenous data from today and tomorrow for all cities and taking average
def get_and_clean_real_time_data():
    cities, station_ids, latitude, longitude, altitude = get_weather_stations()

    start = (datetime.today()).strftime('%Y-%m-%d')
    end = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    today_data = []
    for i in range(len(cities)):
        today_data.append(
            get_today_and_tomorrow_exog_data_request(
                latitude=latitude[i],
                longitude=longitude[i], start=start, end=end,
                columns=['ghi', 'wind_spd', 'temp']))

    average_today = merge_datasets_by_taking_average(today_data, ['ghi', 'wind_spd', 'temp'])

    upsampled_data = average_today.resample('15Min').mean()

    # filling the upsampled datapoints using interpolation
    filledData_spline = upsampled_data.interpolate(method='linear', order=1).round(3)

    # data is available until  23:00, so using last data point to make data until 23:45
    last_datapoint = filledData_spline.loc[[filledData_spline.index[-1]]]
    for i in range(3):
        filledData_spline = filledData_spline.append(last_datapoint, ignore_index=False)
    filledData_spline.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(filledData_spline),
                                            freq='15Min')

    filledData_spline.columns = ["GHI", "windspeed", "temperature"]
    return filledData_spline
