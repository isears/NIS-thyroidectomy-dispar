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
        self.all_proconly_codes = (
            ProcClass.LAPAROSCOPIC.getProcOnlyCodes()
            + ProcClass.OPEN.getProcOnlyCodes()
        )

        logging.info(f"[*] Procedure codes ({len(self.all_proc_codes)}):")
        logging.info(self.all_proc_codes)
        logging.info(f"[*] Diagnosis codes ({len(diagnosis_codes)}):")
        logging.info(diagnosis_codes)
        logging.info(f"[*] Anastomosis codes ({len(self.all_anastomosis_codes)}):")
        logging.info(self.all_anastomosis_codes)
        logging.info(f"[*] Procedure only codes: ({len(self.all_proconly_codes)}):")
        logging.info(self.all_proconly_codes)

    def _get_relevant_procedures(self, df):
        proc_cols = get_proc_cols(df.columns)

        relevant = df[df[proc_cols].isin(self.all_proc_codes).any(axis="columns")]
        relevant = relevant[
            relevant[proc_cols].isin(self.all_anastomosis_codes).any(axis="columns")
        ]

        # Expanded inclusion criteria
        relevant = relevant.append(
            df[
                df[proc_cols].isin(self.all_proconly_codes).any(axis="columns")
                & ~df[proc_cols].isin(self.all_anastomosis_codes).any(axis="columns")
            ]
        )

        return relevant

    def single_file_filter(self, fname):
        df = pd.read_parquet(fname)

        dx_cols = get_dx_cols(df.columns)

        relevant = self._get_relevant_procedures(df)
        relevant = relevant[relevant[dx_cols].isin(diagnosis_codes).any(axis="columns")]

        return relevant

    def single_file_yearcount(self, fname):
        """
        For building fig 1
        """
        df = pd.read_parquet(fname)

        dx_cols = get_dx_cols(df.columns)

        relevant_procs = self._get_relevant_procedures(df)
        relevant_diagnoses = df[df[dx_cols].isin(diagnosis_codes).any(axis="columns")]

        def organaze_as_counts(df: pd.DataFrame):
            counts = df["YEAR"].value_counts().sort_index()
            counts = counts.reset_index()
            counts.columns = ["Year", "Count"]

            return counts

        proc_counts = organaze_as_counts(relevant_procs)
        dx_counts = organaze_as_counts(relevant_diagnoses)

        return proc_counts, dx_counts


if __name__ == "__main__":
    parallel_filter = ParallelFilter()

    with ProcessPoolExecutor(max_workers=16) as executor:
        fnames = glob.glob("data-slow/*.parquet")
        res = list(
            tqdm(
                executor.map(parallel_filter.single_file_filter, fnames),
                total=len(fnames),
            )
        )

    filtered_df = pd.concat(res)

    print(filtered_df)

    # Pyarrow (parquet) complains if this column is dealt with
    filtered_df.HOSPSTCO = filtered_df.HOSPSTCO.astype("str")

    filtered_df.to_parquet("./cache/rectalcancer.parquet", index=False)
