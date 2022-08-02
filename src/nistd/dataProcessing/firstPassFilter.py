"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
import re
from nistd.dataProcessing import thyroidectomy_codes


def get_proc_cols(all_cols):
    icd9_proc_cols = [col for col in all_cols if re.search("^PR[0-9]{1,2}$", col)]
    icd10_proc_cols = [col for col in all_cols if re.search("^I10_PR[0-9]{1,2}$", col)]

    return icd9_proc_cols + icd10_proc_cols


def get_dx_cols(all_cols):
    icd9_cols = [col for col in all_cols if re.search("^DX[0-9]{1,2}$", col)]
    icd10_cols = [col for col in all_cols if re.search("^I10_DX[0-9]{1,2}$", col)]

    return icd9_cols + icd10_cols


if __name__ == "__main__":
    df = pd.DataFrame()

    for fname in glob.glob("./data/*.dta"):
        print(f"[*] Processing {fname}")

        # In theory columns will remain consistent within a file, even if they change between files
        cols = next(pd.read_stata(fname, chunksize=1)).columns
        proc_cols = get_proc_cols(cols)
        dx_cols = get_dx_cols(cols)

        for chunk in pd.read_stata(fname, chunksize=10**6):
            chunk = chunk[
                chunk[proc_cols].isin(thyroidectomy_codes).any(axis="columns")
            ]

            df = df.append(chunk)

        # Monitor memory usage
        df.info()

    df.to_csv("./cache/thyroidectomies.csv", index=False)
