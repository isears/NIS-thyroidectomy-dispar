"""
First-pass filter to isolate thyroidectomies from RAW NIS data
"""
import pandas as pd
import glob
from nistd.dataProcessing import (
    diagnosis_codes,
    get_dx_cols,
    get_proc_cols,
    ProcClass,
    procedure_only_codes,
)
from nistd import logging


if __name__ == "__main__":
    df = pd.DataFrame()

    all_proc_codes = (
        ProcClass.LAPAROSCOPIC.getProcCodes() + ProcClass.OPEN.getProcCodes()
    )
    all_anastomosis_codes = (
        ProcClass.LAPAROSCOPIC.getAnastomosisCodes()
        + ProcClass.OPEN.getAnastomosisCodes()
    )

    logging.info(f"[*] Procedure codes ({len(all_proc_codes)}):")
    logging.info(all_proc_codes)
    logging.info(f"[*] Diagnosis codes ({len(diagnosis_codes)}):")
    logging.info(diagnosis_codes)
    logging.info(f"[*] Anastomosis codes ({len(all_anastomosis_codes)}):")
    logging.info(all_anastomosis_codes)
    logging.info(f"[*] Procedure only codes: ({len(procedure_only_codes)}):")
    logging.info(procedure_only_codes)

    for fname in glob.glob("./data/*.dta"):
        print(f"[*] Processing {fname}")

        # In theory columns will remain consistent within a file, even if they change between files
        cols = next(pd.read_stata(fname, chunksize=1)).columns
        proc_cols = get_proc_cols(cols)
        dx_cols = get_dx_cols(cols)

        for chunk in pd.read_stata(fname, chunksize=10**5):
            relevant = chunk[chunk[proc_cols].isin(all_proc_codes).any(axis="columns")]
            relevant = relevant[
                relevant[proc_cols].isin(all_anastomosis_codes).any(axis="columns")
            ]

            # Expanded inclusion criteria
            relevant = relevant.append(
                chunk[chunk[proc_cols].isin(procedure_only_codes).any(axis="columns")]
            )

            relevant = relevant[
                relevant[dx_cols].isin(diagnosis_codes).any(axis="columns")
            ]

            df = df.append(chunk)

        # Monitor memory usage
        df.info()

    df.to_csv("./cache/rectalcancer.csv", index=False)
