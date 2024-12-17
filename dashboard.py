import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import json

DATE_TRACKER_FILE = "last_fetch_date.json"
DATA_FILE = "bls_data.csv"

st.title("BLS Monthly Data Dashboard")
st.write("This dashboard displays the latest BLS data trends.")

# Check if data is available
if not os.path.exists(DATA_FILE):
    st.error("No data available. Please run data_fetch.py first to fetch the data.")
else:
    data = pd.read_csv(DATA_FILE)
    st.info("Data loaded from local CSV.")

    # Display Last Update Date
    if os.path.exists(DATE_TRACKER_FILE):
        with open(DATE_TRACKER_FILE, "r") as file:
            last_fetch_date = json.load(file)["last_fetch"]
            st.subheader(f"Last Data Update: {last_fetch_date}")

    if not data.empty:
        st.subheader("Data Table")
        st.write(data)

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
