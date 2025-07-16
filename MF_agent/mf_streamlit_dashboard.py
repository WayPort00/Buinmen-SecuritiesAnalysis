import streamlit as st
from mf_data_collector import fetch_data, save_snapshot, get_latest_snapshots, get_diff

API_URL = "https://staticassets.zerodha.com/coin/scheme-portfolio/INF277K01I86.json"

st.title("🧠 Zerodha Scheme Change Tracker")

# Step 1: Fetch current data
with st.spinner("Fetching data from API..."):
    current_df = fetch_data(API_URL)
    save_snapshot(current_df)

# Step 2: Load previous snapshots
prev_df, latest_df = get_latest_snapshots()

if prev_df is None:
    st.warning("Not enough snapshots to compare. Please refresh again after a second call.")
else:
    # Step 3: Show differences
    diff_df = get_diff(prev_df, latest_df)
    if diff_df.empty:
        st.success("No changes detected between last two snapshots.")
    else:
        st.subheader("🔍 Detected Changes")
        st.dataframe(diff_df)
