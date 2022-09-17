"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
from nistd.dataProcessing import diagnosis_codes, get_dx_cols, get_proc_cols, ProcClass


if __name__ == "__main__":
    df = pd.DataFrame()

    all_proc_codes = (
        ProcClass.LAPAROSCOPIC.getProcCodes() + ProcClass.OPEN.getProcCodes()
    )
    all_anastomosis_codes = (
        ProcClass.LAPAROSCOPIC.getAnastomosisCodes() + ProcClass.OPEN.getProcCodes()
    )

    print("[*] Procedure codes:")
    print(all_proc_codes)
    print("[*] Diagnosis codes:")
    print(diagnosis_codes)
    print("[*] Anastomosis codes:")
    print(all_anastomosis_codes)

    for fname in glob.glob("./data/*.dta"):
        print(f"[*] Processing {fname}")

        # In theory columns will remain consistent within a file, even if they change between files
        cols = next(pd.read_stata(fname, chunksize=1)).columns
        proc_cols = get_proc_cols(cols)
        dx_cols = get_dx_cols(cols)

        for chunk in pd.read_stata(fname, chunksize=10**5):
            chunk = chunk[chunk[proc_cols].isin(all_proc_codes).any(axis="columns")]
            chunk = chunk[
                chunk[proc_cols].isin(all_anastomosis_codes).any(axis="columns")
            ]
            chunk = chunk[chunk[dx_cols].isin(diagnosis_codes).any(axis="columns")]

            df = df.append(chunk)

        # Monitor memory usage
        df.info()

    df.to_csv("./cache/rectalcancer.csv", index=False)
