import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from nistd.dataProcessing import categorical_lookup


if __name__ == "__main__":
    filtered_df = pd.read_parquet("cache/filtered.parquet")
    plottable_df = filtered_df[["YEAR", "HOSP_DIVISION"]]
    plottable_df["HOSP_DIVISION"] = plottable_df["HOSP_DIVISION"].apply(
        lambda x: categorical_lookup["HOSP_DIVISION"][int(x) - 1]
    )

    plottable_df = plottable_df.groupby("HOSP_DIVISION").YEAR.value_counts().unstack(0)

    plottable_df = pd.melt(plottable_df, ignore_index=False).reset_index()

    plottable_df = plottable_df.rename(
        columns={
            "YEAR": "Year",
            "HOSP_DIVISION": "Hospital Division",
            "value": "Number of Procedures",
        }
    )
    sns.set_theme()
    plt.figure(figsize=(10, 10))
    ax = sns.lineplot(
        data=plottable_df, x="Year", y="Number of Procedures", hue="Hospital Division"
    )

    # ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.set_title("Thyroidectomies by Year, per Region")

    plt.savefig("results/fig2.png")
