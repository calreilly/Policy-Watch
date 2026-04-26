import nfl_data_py as nfl
import pandas as pd
import sys

def main():
    print("Fetching drafts...", flush=True)
    try:
        drafts = nfl.import_draft_picks(years=[y for y in range(2000, 2024)])
        print("Drafts columns:", drafts.columns.tolist(), flush=True)
    except Exception as e:
        print(f"Error fetching drafts: {e}")

    print("Fetching combine...", flush=True)
    try:
        combine = nfl.import_combine_data([y for y in range(2000, 2024)])
        print("Combine columns:", combine.columns.tolist(), flush=True)
    except Exception as e:
        print(f"Error fetching combine: {e}")

if __name__ == "__main__":
    main()
