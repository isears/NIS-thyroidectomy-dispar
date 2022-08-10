import pandas as pd
from nistd.dataProcessing import get_dtypes
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filtered_df = pd.read_csv("cache/filtered.csv", dtype=get_dtypes(), index_col=0)

    medians_by_year = filtered_df[["YEAR", "LOS"]].groupby("YEAR").median()
    medians_by_year.reset_index(inplace=True)
    medians_by_year["YEAR"] = medians_by_year["YEAR"].astype(int)
    medians_by_year = medians_by_year.rename(
        {"YEAR": "Year", "LOS": "Median Length of Stay"}, axis=1
    )

    sns.set_theme()
    ax = sns.lineplot(
        x="Year", y="Median Length of Stay", data=medians_by_year, color="b"
    )

    # ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.set_title("Median Length of Stay for Thyroidectomy by Year")

    plt.savefig("results/fig2.png")
