import streamlit as st
import os
import pandas as pd
from utils import get_latest_snapshots, get_diff, DIFF_DIR

st.set_page_config(layout="wide")
st.title("📊 Mutual Fund Portfolio Change Tracker")

# Get list of scheme folders
scheme_codes = sorted(os.listdir("data"))
scheme = st.selectbox("Select Mutual Fund Scheme Code", scheme_codes)

prev_df, latest_df = get_latest_snapshots(scheme)

if prev_df is None:
    st.warning("Not enough data to compare yet. Try running monitor_all.py again.")
else:
    diff_df = get_diff(prev_df, latest_df)
    if diff_df.empty:
        st.success("No changes detected between the latest snapshots.")
    else:
        st.subheader("🔍 Detected Differences")
        st.dataframe(diff_df, use_container_width=True)

        # Optionally display latest snapshot
        with st.expander("📁 View Latest Snapshot"):
            st.dataframe(latest_df, use_container_width=True)