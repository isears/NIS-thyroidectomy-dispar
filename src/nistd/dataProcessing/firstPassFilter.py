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
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm


class ParallelFilter:
    def __init__(self) -> None:
        logging.info("Initializing parallel filter...")
        self.all_proc_codes = (
            ProcClass.LAPAROSCOPIC.getProcCodes() + ProcClass.OPEN.getProcCodes()
        )
        self.all_anastomosis_codes = (
            ProcClass.LAPAROSCOPIC.getAnastomosisCodes()
            + ProcClass.OPEN.getAnastomosisCodes()
        )

        logging.info(f"[*] Procedure codes ({len(self.all_proc_codes)}):")
        logging.info(self.all_proc_codes)
        logging.info(f"[*] Diagnosis codes ({len(diagnosis_codes)}):")
        logging.info(diagnosis_codes)
        logging.info(f"[*] Anastomosis codes ({len(self.all_anastomosis_codes)}):")
        logging.info(self.all_anastomosis_codes)
        logging.info(f"[*] Procedure only codes: ({len(procedure_only_codes)}):")
        logging.info(procedure_only_codes)

    def handle_single_file(self, fname):
        df = pd.read_parquet(fname)

        proc_cols = get_proc_cols(df.columns)
        dx_cols = get_dx_cols(df.columns)

        relevant = df[df[proc_cols].isin(self.all_proc_codes).any(axis="columns")]
        relevant = relevant[
            relevant[proc_cols].isin(self.all_anastomosis_codes).any(axis="columns")
        ]

        # Expanded inclusion criteria
        relevant = relevant.append(
            df[df[proc_cols].isin(procedure_only_codes).any(axis="columns")]
        )

        relevant = relevant[relevant[dx_cols].isin(diagnosis_codes).any(axis="columns")]

        return relevant


if __name__ == "__main__":
    parallel_filter = ParallelFilter()

    with ProcessPoolExecutor(max_workers=16) as executor:
        fnames = glob.glob("data-slow/*.parquet")
        res = list(
            tqdm(
                executor.map(parallel_filter.handle_single_file, fnames),
                total=len(fnames),
            )
        )

    filtered_df = pd.concat(res)

    print(filtered_df)

    # Pyarrow (parquet) complains if this column is dealt with
    filtered_df.HOSPSTCO = filtered_df.HOSPSTCO.astype("str")

    filtered_df.to_parquet("./cache/rectalcancer.parquet", index=False)
