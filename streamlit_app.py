import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

# File to store the last fetch date
DATE_TRACKER_FILE = "last_fetch_date.json"
DATA_FILE = "bls_data.csv"

# Function to check the last update date
def should_update_data():
    if not os.path.exists(DATE_TRACKER_FILE):
        return True
    with open(DATE_TRACKER_FILE, "r") as file:
        data = json.load(file)
        last_fetch_date = datetime.datetime.strptime(data["last_fetch"], "%Y-%m-%d")
    return (datetime.datetime.now() - last_fetch_date).days >= 30

# Function to save the current fetch date
def update_fetch_date():
    with open(DATE_TRACKER_FILE, "w") as file:
        json.dump({"last_fetch": datetime.datetime.now().strftime("%Y-%m-%d")}, file)

# Function to fetch and process data
def fetch_bls_data():
    headers = {'Content-type': 'application/json'}
    current_year = datetime.datetime.now().year
    last_year = current_year - 1
    data = json.dumps({
        "seriesid": ["LNS14000000", "CES0000000001", "LNS11000000", "LNS12000000", "LNS13000000", "CES0500000002", "CES0500000007"],
        "startyear": str(last_year),
        "endyear": str(current_year)
    })
    
    # Define SERIES_NAMES inside the function
    SERIES_NAMES = { 
        "LNS14000000": "Unemployment Rate",
        "CES0000000001": "All Employees, Total Nonfarm",
        "LNS11000000": "Civilian Labor Force Level",
        "LNS12000000": "Employment Level",
        "LNS13000000": "Unemployment Level",
        "CES0500000002": "Total Private Production and Nonsupervisory Employees",
        "CES0500000007": "Average Hourly Earnings of Production and Nonsupervisory Employees"
    }

    response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(response.text)

    all_series_data = []
    for series in json_data.get('Results', {}).get('series', []):
        seriesId = series['seriesID']
        for item in series['data']:
            if 'M01' <= item['period'] <= 'M12':  # Monthly data only
                all_series_data.append({
                    "Series ID": seriesId,
                    "Year": int(item['year']),
                    "Month": int(item['period'][1:]),
                    "Value": float(item['value'])
                })

    if all_series_data:
        df = pd.DataFrame(all_series_data)
        df.to_csv(DATA_FILE, index=False)  # Save data locally
        update_fetch_date()
        return df
    else:
        st.error("No data was returned from the BLS API. Check the API request.")
        return pd.DataFrame()

# After this, you'd have code that either reads the existing CSV or calls fetch_bls_data()
