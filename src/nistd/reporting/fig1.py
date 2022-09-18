import pandas as pd
from nistd.dataProcessing import get_dtypes
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

if __name__ == "__main__":
    filtered_df = pd.read_csv(
        "cache/filtered_OPEN.csv", dtype=get_dtypes(), index_col=0
    )
    filtered_df = filtered_df.append(
        pd.read_csv("cache/filtered_LAPAROSCOPIC.csv", dtype=get_dtypes(), index_col=0)
    )

    counts = filtered_df["YEAR"].value_counts().sort_index()
    counts_df = counts.reset_index()
    counts_df.columns = ["Year", "Number of Procedures"]

    sns.set_theme()
    ax = sns.lineplot(x="Year", y="Number of Procedures", data=counts_df, color="b")
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Procedures by Year")

    plt.savefig("results/fig1.png")
