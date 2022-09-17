"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
from nistd.dataProcessing import (
    proc_codes,
    diagnosis_codes,
    anastomosis_codes,
    get_dx_cols,
    get_proc_cols,
)


if __name__ == "__main__":
    df = pd.DataFrame()

    print("[*] Procedure codes:")
    print(proc_codes)
    print("[*] Diagnosis codes:")
    print(diagnosis_codes)
    print("[*] Anastomosis codes:")
    print(anastomosis_codes)

    for fname in glob.glob("./data/*.dta"):
        print(f"[*] Processing {fname}")

        # In theory columns will remain consistent within a file, even if they change between files
        cols = next(pd.read_stata(fname, chunksize=1)).columns
        proc_cols = get_proc_cols(cols)
        dx_cols = get_dx_cols(cols)

        for chunk in pd.read_stata(fname, chunksize=10**5):
            chunk = chunk[chunk[proc_cols].isin(proc_codes).any(axis="columns")]
            chunk = chunk[chunk[proc_cols].isin(anastomosis_codes).any(axis="columns")]
            chunk = chunk[chunk[dx_cols].isin(diagnosis_codes).any(axis="columns")]

            df = df.append(chunk)

        # Monitor memory usage
        df.info()

    df.to_csv("./cache/rectalcancer.csv", index=False)
