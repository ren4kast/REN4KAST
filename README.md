# Percentage of Renewables Energy Generation Day-Ahead Forecasting Service 
## Description
Forecasting percentage of renewable energy generation for the Day-Ahead for Germany.


## Requirements:
Install requirements using the following command
```bash
pip install -r requirements.txt
```


# Usage:

## Flask Server:
Use the following code to start the server:
```bash
from main import run_server
run_server()
```

Then send a GET request to `/getForecasts` endpoint. 
It returns a CSV file containing day-ahead forecasts.

## Google Colab:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1xNS2hNAQXoVFncymC0HRh8YThbVVAsGn)

