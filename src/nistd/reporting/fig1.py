import pandas as pd
from nistd.dataProcessing import (
    get_dtypes,
    get_proc_cols,
    get_dx_cols,
    ProcClass,
    diagnosis_codes,
)
from nistd import logging
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import glob
import os


def buildcache():
    proc_df = pd.DataFrame()
    proc_anast_df = pd.DataFrame()
    dx_df = pd.DataFrame()

    all_proc_codes = (
        ProcClass.LAPAROSCOPIC.getProcCodes() + ProcClass.OPEN.getProcCodes()
    )
    all_anastomosis_codes = (
        ProcClass.LAPAROSCOPIC.getAnastomosisCodes() + ProcClass.OPEN.getProcCodes()
    )

    for fname in glob.glob("./data/*.dta"):
        logging.info(fname)

        cols = next(pd.read_stata(fname, chunksize=1)).columns
        proc_cols = get_proc_cols(cols)
        dx_cols = get_dx_cols(cols)
        used_cols = ["YEAR"] + proc_cols + dx_cols

        for chunk in pd.read_stata(fname, columns=used_cols, chunksize=10**5):
            proc_chunk = chunk[chunk[proc_cols].isin(all_proc_codes).any("columns")]
            proc_anast_chunk = proc_chunk[
                proc_chunk[proc_cols].isin(all_anastomosis_codes).any("columns")
            ]

            dx_chunk = chunk[chunk[dx_cols].isin(diagnosis_codes).any("columns")]

            proc_df = proc_df.append(proc_chunk)
            proc_anast_df = proc_anast_df.append(proc_anast_chunk)
            dx_df = dx_df.append(dx_chunk)

    def organaze_as_counts(df: pd.DataFrame, count_col_name: str):
        counts = df["YEAR"].value_counts().sort_index()
        counts = counts.reset_index()
        counts.columns = ["Year", count_col_name]

        return counts

    proc_counts = organaze_as_counts(proc_df, "# Procedures")
    proc_anast_counts = organaze_as_counts(proc_anast_df, "# Procedures + Anastomosis")
    dx_counts = organaze_as_counts(dx_df, "# Diagnoses")

    combined_counts = pd.merge(proc_counts, proc_anast_counts, how="left", on="Year")
    combined_counts = pd.merge(combined_counts, dx_counts, how="left", on="Year")

    combined_counts.to_csv("cache/fig1counts.csv", index=False)

    return combined_counts


if __name__ == "__main__":
    if not os.path.exists("cache/fig1counts.csv"):
        logging.info("Cache not found, rebuilding...")
        combined_counts = buildcache()
    else:
        logging.info("Reusing cache found at cache/fig1counts.csv")
        combined_counts = pd.read_csv("cache/fig1counts.csv")

    combined_counts = combined_counts.set_index("Year")
    sns.set_theme()
    ax = sns.lineplot(data=combined_counts)
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Procedures and Diagnoses by Year")

    plt.savefig("results/fig1.png")
