import streamlit as st
import os
from utils import get_latest_snapshots, get_diff

st.set_page_config(layout="wide")
st.title("📊 Mutual Fund Portfolio Change Tracker")

# Fetch and display diffs for all schemes in a single view
scheme_dirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]

diffs_found = False
for scheme in sorted(scheme_dirs):
    prev_df, latest_df = get_latest_snapshots(scheme)
    if prev_df is None:
        continue
    diff_df = get_diff(prev_df, latest_df)
    if not diff_df.empty:
        diffs_found = True
        st.markdown(f"---\n### 🔍 Changes for **{scheme}**")
        st.dataframe(diff_df, use_container_width=True)

if not diffs_found:
    st.success("✅ No changes detected across all mutual funds.")
