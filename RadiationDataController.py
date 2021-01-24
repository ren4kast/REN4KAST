import requests
import pandas as pd


# getting historical radiation data from soda (for GHI)
def get_request_soda(latitude, longitude, altitude, start, end, columns):
    url = 'http://www.soda-is.com/service/wps?Service=WPS&Request=Execute&Identifier=get_cams_radiation&version=1.0.0&DataInputs=latitude={};longitude={};altitude={};date_begin={};date_end={};time_ref=UT;summarization=PT15M;username=amirhoseinshafieyoun%2540gmail.com&RawDataOutput=irradiation'.format(
        latitude, longitude, altitude, start, end)
    content = requests.get(url).content
    # removing begining description and wiritng to file
    content = content[content.decode("utf-8").find("Observation period;TOA;Clear sky GHI"):]
    df = pd.DataFrame([x.split(';') for x in content.decode("utf-8").split('\n')[1:]],
                      columns=[x for x in content.decode("utf-8").split('\n')[0].split(';')])
    df.index = pd.date_range(start="{} 00:00:00".format(start), periods=len(df), freq='15Min')
    df.index.name = 'time'

    # removing the last empty line
    df = df.drop(df.index[-1])

    # changing type from non-type to float. because later we want to calculate the average among all cities
    df[columns] = df[columns].apply(pd.to_numeric)
    # replacing missing values with the previous non-missing value
    df[columns] = df[columns].ffill()
    return df


# Getting historical radiation data for all cities
def bulk_get_radiation_data(cities, start, end, latitude, longitude, altitude):
    ghi_data = []

    for i in range(len(cities)):
        # getting GHI from Soda
        ghi_data.append(get_request_soda(latitude=latitude[i],
                                         longitude=longitude[i], altitude=altitude[i], start=start, end=end,
                                         columns=["GHI"]))
    return ghi_data
