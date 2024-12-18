import requests
import pandas as pd
from datetime import datetime
import os
API_KEY = "YOUR_API_KEY_HERE"
SERIES_IDS = {
"Non-Farm Workers": "CES0000000001",
"Unemployment Rate": "LNS14000000",
}
def fetch_bls_data(series_id, start_year, end_year):
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
payload = {
"seriesid": [series_id],
"startyear": start_year,
"endyear": end_year,
"registrationkey": API_KEY,
}
response = requests.post(url, json=payload)
if response.status_code == 200:
data = response.json()
if data["status"] == "REQUEST_SUCCEEDED":
return pd.DataFrame(data["Results"]["series"][0]["data"])
return pd.DataFrame()
def convert_period_to_date(year, period):
if period.startswith("M"):
return f"{year}-{period[1:].zfill(2)}-01"
elif period.startswith("Q"):
quarter_to_month = {"Q01": "01", "Q02": "04", "Q03": "07", "Q04": "10"}
return f"{year}-{quarter_to_month[period]}-01"
return None
def collect_data():
current_year = datetime.now().year
start_year = current_year - 1
all_data = []
for name, series_id in SERIES_IDS.items():
print(f"Fetching data for {name} ({series_id})...")
df = fetch_bls_data(series_id, start_year, current_year)
if not df.empty and set(["year", "period", "value"]).issubset(df.columns):
df["date"] = df.apply(lambda row: convert_period_to_date(row["year"], row["period"]), axis=1)
df = df.dropna(subset=["date"])
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df["series"] = name
df = df[["date", "value", "series"]]
all_data.append(df)
else:
print(f"No data found for {name}.")
if all_data:
return pd.concat(all_data, ignore_index=True)
return pd.DataFrame()
if __name__ == "__main__":
data = collect_data()
if not data.empty:
data.to_csv("labor_statistics.csv", index=False)
print("Data saved to labor_statistics.csv")
else:
print("No data collected.")

