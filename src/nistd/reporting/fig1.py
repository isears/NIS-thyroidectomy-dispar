import pandas as pd
from nistd.dataProcessing.firstPassFilter import ParallelFilter
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import glob
from nistd import logging
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

if __name__ == "__main__":
    pf = ParallelFilter()

    with ProcessPoolExecutor(max_workers=16) as executor:
        fnames = glob.glob("data-slow/*.parquet")
        res = list(
            tqdm(
                executor.map(pf.single_file_yearcount, fnames),
                total=len(fnames),
            )
        )

    allcounts_procs = pd.concat([proc_df for proc_df, _, _ in res]).rename(
        columns={"Count": "Procedures"}
    )

    allcounts_procdx = pd.concat([procdx_df for _, procdx_df, _ in res]).rename(
        columns={"Count": "Procedures with Diagnoses"}
    )

    allcounts_dx = pd.concat([dx_df for _, _, dx_df in res]).rename(
        columns={"Count": "Diagnoses"}
    )

    allcounts_procs = allcounts_procs.groupby("Year").sum()
    allcounts_procdx = allcounts_procdx.groupby("Year").sum()
    allcounts_dx = allcounts_dx.groupby("Year").sum()

    allcounts = pd.merge(
        allcounts_procs, allcounts_dx, how="left", left_index=True, right_index=True
    )

    allcounts = pd.merge(
        allcounts, allcounts_procdx, how="left", left_index=True, right_index=True
    )

    sns.set_theme()
    ax = sns.lineplot(data=allcounts)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Procedures and Diagnoses by Year")

    plt.savefig("results/fig1.png")

    print("[+] Done")
