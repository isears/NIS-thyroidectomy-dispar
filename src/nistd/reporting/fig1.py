import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    filtered_df = pd.read_parquet("cache/filtered.parquet")
    counts = filtered_df["YEAR"].value_counts().sort_index()
    counts_df = counts.reset_index()
    counts_df.columns = ["Year", "Number of Procedures"]

    sns.set_theme()
    ax = sns.barplot(x="Year", y="Number of Procedures", data=counts_df, color="b")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.set_title("Thyroidectomy Procedures by Year")

    plt.savefig("results/fig1.png")
