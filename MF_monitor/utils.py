import os
import re
import pandas as pd
import requests
from datetime import datetime

DATA_DIR = "data"
DIFF_DIR = "diffs"
COLUMNS = [
    "Units (in Crores)", "Company Name", "Sector", "Type",
    "Quantity", "Weight (%)", "Market Price", "Notes"
]

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DIFF_DIR, exist_ok=True)

def extract_scheme_code(url):
    match = re.search(r'([^/]+)\.json$', url)
    print(match)
    if match:
        print(match.group())
        return match.group(1)

def fetch_data(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json().get("data", [])
    df = pd.DataFrame(data, columns=COLUMNS)
    return df

def save_snapshot(df, scheme_code):
    folder = os.path.join(DATA_DIR, scheme_code)
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"snapshot_{timestamp}.csv")
    df.to_csv(filename, index=False)
    return filename

def get_latest_snapshots(scheme_code):
    folder = os.path.join(DATA_DIR, scheme_code)
    if not os.path.exists(folder):
        return None, None
    files = sorted([f for f in os.listdir(folder) if f.endswith(".csv")], reverse=True)
    if len(files) < 2:
        return None, None
    latest = pd.read_csv(os.path.join(folder, files[0]))
    previous = pd.read_csv(os.path.join(folder, files[1]))
    return previous, latest

def get_diff(prev_df, new_df):
    merged = new_df.merge(prev_df, indicator=True, how='outer')
    changed = merged[merged['_merge'] != 'both']
    return changed.drop(columns=['_merge'])

def save_diff(diff_df, scheme_code):
    if diff_df.empty:
        return None
    folder = os.path.join(DIFF_DIR, scheme_code)
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"diff_{timestamp}.csv")
    diff_df.to_csv(filename, index=False)
    return filename