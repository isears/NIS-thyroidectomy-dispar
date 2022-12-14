import pandas as pd
from nistd.dataProcessing import get_dtypes
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filtered_df = pd.read_csv("cache/filtered.csv", dtype=get_dtypes(), index_col=0)
    counts = filtered_df["YEAR"].value_counts().sort_index()
    counts_df = counts.reset_index()
    counts_df.columns = ["Year", "Number of Procedures"]

    sns.set_theme()
    ax = sns.barplot(x="Year", y="Number of Procedures", data=counts_df, color="b")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.set_title("Thyroidectomy Procedures by Year")

    plt.savefig("results/fig1.png")
