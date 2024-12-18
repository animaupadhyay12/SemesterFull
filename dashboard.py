import streamlit as st
import pandas as pd
import os

DATA_FILE = "labor_statistics.csv"

st.title("Labor Statistics Dashboard")

# Check if the data file exists
if not os.path.exists(DATA_FILE):
    st.error("Data file not found. Please run 'fetch_data.py' to collect the data.")
else:
    # Load data
    data = pd.read_csv(DATA_FILE)
    data["date"] = pd.to_datetime(data["date"])
    
    st.write("## Overview")
    st.write("This dashboard presents labor market data such as total non-farm workers and unemployment rates.")
    
    # Let users select which series to view
    series_options = sorted(data["series"].unique())
    selected_series = st.multiselect("Select the data series to display", series_options, default=series_options)

    if selected_series:
        filtered_data = data[data["series"].isin(selected_series)]

        # Add a date filter, if desired
        start_date = st.date_input("Start Date", value=filtered_data["date"].min())
        end_date = st.date_input("End Date", value=filtered_data["date"].max())
        
        filtered_data = filtered_data[(filtered_data["date"] >= pd.to_datetime(start_date)) & (filtered_data["date"] <= pd.to_datetime(end_date))]

        # Display raw data if requested
        if st.checkbox("Show raw data"):
            st.subheader("Raw Data")
            st.write(filtered_data)

        # Create a line chart
        st.subheader("Time Series Chart")
        chart_data = filtered_data.pivot(index="date", columns="series", values="value")
        st.line_chart(chart_data)

        # Some basic statistics
        st.subheader("Summary Statistics")
        st.write(filtered_data.groupby("series")["value"].describe())
    else:
        st.warning("Please select at least one series to display.")
