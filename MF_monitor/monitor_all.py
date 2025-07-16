from utils import fetch_data, extract_scheme_code, save_snapshot, get_latest_snapshots, get_diff, save_diff

with open("urls/mutual_fund_urls.txt") as f:
    urls = [line.strip() for line in f if line.strip()]

for url in urls:
    try:
        print(url)
        scheme_code = extract_scheme_code(url)
        if not scheme_code:
            print(f"⚠️  Could not extract scheme code from URL: {url}")
            continue

        df = fetch_data(url)
        save_snapshot(df, scheme_code)

        prev_df, latest_df = get_latest_snapshots(scheme_code)
        if prev_df is not None:
            diff = get_diff(prev_df, latest_df)
            if not diff.empty:
                save_diff(diff, scheme_code)
                print(f"✅ Changes detected in {scheme_code}")
            else:
                print(f"ℹ️  No change for {scheme_code}")
        else:
            print(f"📥 First snapshot saved for {scheme_code}")

    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
