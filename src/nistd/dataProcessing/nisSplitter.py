"""
Just split the .statas to parquet files with 100,000 entries each
"""
import pandas as pd
import glob


if __name__ == "__main__":
    fname = "./data/NIS_2000_Full.dta"

    for fname in glob.glob("./data/*.dta"):
        fid = fname.split("/")[-1].split(".")[0]
        print(f"Processing file: {fid}")

        for idx, chunk in enumerate(pd.read_stata(fname, chunksize=100000)):
            chunk.to_parquet(f"data-slow/{fid}_{idx:04d}.parquet", index=False)
