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
        "seriesid": [
            "LNS14000000", "CES0000000001", "LNS11000000", 
            "LNS12000000", "LNS13000000", "CES0500000002", "CES0500000007"
        ],
        "startyear": str(last_year),
        "endyear": str(current_year)
    })
    
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    
    # Inspect the raw API response
    st.write(json_data)

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

# Load data if available, or fetch it
if not os.path.exists(DATA_FILE) or should_update_data():
    st.info("Fetching updated data...")
    data = fetch_bls_data()
    if not data.empty:
        st.success("Data successfully updated!")
else:
    data = pd.read_csv(DATA_FILE)
    st.info("Data is up to date.")

# Dashboard Layout
st.title("BLS Monthly Data Dashboard")
st.write("This dashboard displays the latest BLS data trends.")

# Display Last Update Date
if os.path.exists(DATE_TRACKER_FILE):
    with open(DATE_TRACKER_FILE, "r") as file:
        last_fetch_date = json.load(file)["last_fetch"]
        st.subheader(f"Last Data Update: {last_fetch_date}")

# Data Table Display
if not data.empty:
    st.subheader("Data Table")
    st.write(data)  # Display data using st.write for compatibility

    # Visualization
    st.subheader("Data Visualization")
    series_ids = data['Series ID'].unique()

    for series_id in series_ids:
        st.write(f"### Series: {series_id}")
        series_data = data[data['Series ID'] == series_id].copy()
        series_data['Date'] = pd.to_datetime(series_data[['Year', 'Month']].assign(day=1))
        series_data = series_data.sort_values('Date')

        # Plot using Matplotlib
        fig, ax = plt.subplots()
        ax.plot(series_data['Date'], series_data['Value'], marker='o', linestyle='-')
        ax.set_title(f"Trend for Series {series_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.grid(True)
        st.pyplot(fig)
else:
    st.warning("No data available to display.")

