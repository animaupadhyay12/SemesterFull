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
