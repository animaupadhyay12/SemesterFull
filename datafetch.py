import requests
import pandas as pd
from datetime import datetime
import os

# Replace this with your actual API key from BLS
API_KEY = "YOUR_API_KEY_HERE"

# Dictionary of BLS series IDs to fetch
SERIES_IDS = {
    "Non-Farm Workers": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
    # Add more series if needed
}

def fetch_bls_data(series_id, start_year, end_year):
    """Fetch data from BLS API for a given series and time range."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": API_KEY,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "REQUEST_SUCCEEDED":
            return pd.DataFrame(data["Results"]["series"][0]["data"])
    return pd.DataFrame()

def convert_period_to_date(year, period):
    """Convert BLS period to a proper datetime string."""
    if period.startswith("M"):
        # Monthly data
        return f"{year}-{period[1:].zfill(2)}-01"
    elif period.startswith("Q"):
        # Quarterly data
        quarter_to_month = {"Q01": "01", "Q02": "04", "Q03": "07", "Q04": "10"}
        return f"{year}-{quarter_to_month[period]}-01"
    return None

def collect_data():
    """Collect data for all series over the last year and current year."""
    current_year = datetime.now().year
    start_year = current_year - 1  # At least one year of previous data

    all_data = []
    for name, series_id in SERIES_IDS.items():
        print(f"Fetching data for {name} ({series_id})...")
        df = fetch_bls_data(series_id, start_year, current_year)
        if not df.empty and {"year", "period", "value"}.issubset(df.columns):
            # Convert periods to actual dates
            df["date"] = df.apply(lambda row: convert_period_to_date(row["year"], row["period"]), axis=1)
            df.dropna(subset=["date"], inplace=True)

            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df["series"] = name
            df = df[["date", "value", "series"]]
            all_data.append(df)
        else:
            print(f"No data found for {name}.")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Sort by date for convenience
        final_df.sort_values(by="date", inplace=True)
        return final_df
    return pd.DataFrame()

if __name__ == "__main__":
    data = collect_data()
    if not data.empty:
        data.to_csv("labor_statistics.csv", index=False)
        print("Data saved to labor_statistics.csv")
    else:
        print("No data collected.")
