import os
import pandas as pd
import requests
from datetime import datetime

COLUMNS = [
    "Units (in Crores)", "Company Name", "Sector", "Type",
    "Quantity", "Weight (%)", "Market Price", "Notes"
]

DATA_DIR = "MF_agent/data_timestamped"
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_data(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json().get("data", []) ### Data is response field
    df = pd.DataFrame(data, columns=COLUMNS)
    return df


def save_snapshot(df):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DATA_DIR}/snapshot_{timestamp}.csv"
    df.to_csv(filename, index=False)
    return filename


def get_latest_snapshots():
    snapshots = sorted(
        [f for f in os.listdir(DATA_DIR) if f.startswith("snapshot_")],
        reverse=True
    )
    if len(snapshots) < 2:
        return None, None

    latest = pd.read_csv(os.path.join(DATA_DIR, snapshots[0]))
    previous = pd.read_csv(os.path.join(DATA_DIR, snapshots[1]))
    return previous, latest


def get_diff(prev_df, new_df):
    merged = new_df.merge(prev_df, indicator=True, how='outer')
    changed = merged[merged['_merge'] != 'both']
    return changed.drop(columns=['_merge'])
