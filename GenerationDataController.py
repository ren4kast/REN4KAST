from entsoe import EntsoePandasClient
import pandas as pd

# Getting generation data from entsoe
def get_entsoe_data(start, end, expected_length):
    # Defining entsoe key
    client = EntsoePandasClient("94aa148a-330b-4eee-ba0c-8a5eb0b17825")
    country_code = 'DE'  # Germany

    # methods that return Pandas Series
    # 'documentType': 'A75',
    # 'processType': 'A16',
    # https://github.com/EnergieID/entsoe-py/blob/5d176699472744c1acef546410826da6549112cf/entsoe/entsoe.py#L270
    entsoe_data = client.query_generation(country_code, start=start, end=end, psr_type=None)

    # converting to GMT
    entsoe_data.index = entsoe_data.index.tz_convert('Etc/GMT')

    # Fixing missing and null values for last few datapoints (today)
    last_dp = entsoe_data.loc[[entsoe_data.index[-1]]]
    for i in range(expected_length - len(entsoe_data)):
        entsoe_data = entsoe_data.append(last_dp, ignore_index=False)
    entsoe_data = entsoe_data.ffill()

    # changing type from non-type to float. because later we want to calculate the average among all cities
    entsoe_data = entsoe_data.apply(pd.to_numeric)
    return entsoe_data


# Calculate renewables percentage
def calculate_renewables_percentage(start, end, expected_length):
    #entsoe_data = get_entsoe_data(start, end, expected_length)
    # asserting that the number of rows
    assert expected_length == len(entsoe_data), "Number of rows did NOT match! {} vs. {}".format(expected_length,
                                                                                                 len(entsoe_data))
    # updating the index
    entsoe_data.index = pd.date_range(start="{} 00:00:00".format(start.strftime('%Y-%m-%d')), periods=len(entsoe_data),
                                      freq='15Min')
    entsoe_data.index.name = 'time'

    generation_data = entsoe_data
    sumBioMassAndHydro = generation_data['Biomass'] + generation_data['Hydro Run-of-river and poundage'] + \
                         generation_data['Hydro Pumped Storage'] + generation_data[
                             'Hydro Water Reservoir'] + generation_data['Geothermal'] + generation_data['Waste']

    sumOthers = generation_data['Wind Offshore'] + generation_data['Wind Onshore'] + generation_data['Solar'] + \
                generation_data['Nuclear'] + generation_data['Fossil Brown coal/Lignite'] + generation_data[
                    'Fossil Hard coal'] + generation_data['Fossil Gas'] + \
                generation_data['Other'] + generation_data['Other renewable'] + generation_data['Fossil Oil'] + \
                generation_data['Fossil Coal-derived gas']

    calcTotal = sumBioMassAndHydro + sumOthers

    RenForecast = generation_data.drop(columns=['Biomass', 'Fossil Brown coal/Lignite', 'Fossil Gas',
                                                'Fossil Hard coal', 'Fossil Oil','Fossil Coal-derived gas', 'Geothermal', 'Hydro Pumped Storage',
                                                'Hydro Run-of-river and poundage', 'Hydro Water Reservoir', 'Nuclear',
                                                'Other', 'Waste', #('Other renewable', 'Actual Consumption'),
                                                ('Solar', 'Actual Consumption'), ('Other renewable', 'Actual Consumption'),
                                                ('Wind Onshore', 'Actual Consumption')])

    RenForecast.insert(0, "calcTotal", calcTotal["Actual Aggregated"], True)
    RenForecast.insert(1, "sumBioMassAndHydro", sumBioMassAndHydro["Actual Aggregated"], True)
    
    RenForecast.columns = ["calcTotal", "sumBioMassAndHydro", "Other renewable", "Solar", "Wind Offshore",
                           "Wind Onshore"]

    renewablesPercentage = pd.DataFrame(columns=['percentage'], index=[RenForecast.index])
    forecast = RenForecast.copy()
    for index, row in forecast.iterrows():
        if (row["sumBioMassAndHydro"].all == 0.0):
            print(row["sumBioMassAndHydro"])

    renewablesPercentage = pd.DataFrame(columns=['percentage'], index=[RenForecast.index])
    forecast = RenForecast.copy()
    for index, row in forecast.iterrows():
        sum_renewables = row['sumBioMassAndHydro'] + row['Other renewable'] + row['Solar'] + row['Wind Offshore'] + row[
            'Wind Onshore']
        prct = sum_renewables / row['calcTotal']
        prct = prct * 100
        renewablesPercentage.loc[index] = [round(prct, 2)]

    renewablesPercentage.index = entsoe_data.index
    return renewablesPercentage
