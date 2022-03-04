# Percentage of Renewables Energy Generation Day-Ahead Forecasting Service 
## Description
Forecasting percentage of renewable energy generation for the Day-Ahead for Germany.

Please note that this service is supposed to be used between 23:01 and  23:59.


## Requirements:
Install requirements using the following command
```bash
pip install -r requirements.txt
```


# Usage:

## Get Forecasts:
Use the following code to get forecasts for the day ahead (between 23:01 and 23:59):
```bash
from main import forecast_v2
forecast_v2()
```
It returns a pandas Dataframe containing day-ahead forecasts.

## Google Colab:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1T1HBMGUFbR2EPXWf2ZZvzS0yYCfu6OfB)

# Contributors
* Prof. Doc. Robert Basmadjian
* Amirhossein Shaafieyoun

# Related Articles
* [Day-Ahead Forecasting of the Percentage of Renewables Based on Time-Series Statistical Methods](https://www.mdpi.com/1996-1073/14/21/7443)
* ARIMA-based Forecasts for the Share of Renewable Energy Sources: The Case Study of Germany
