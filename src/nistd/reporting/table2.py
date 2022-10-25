import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from nistd.dataProcessing import categorical_lookup


if __name__ == "__main__":
    filtered_df = pd.read_parquet("cache/filtered.parquet")
    table_df = filtered_df[["YEAR", "HOSP_DIVISION"]]
    table_df["HOSP_DIVISION"] = table_df["HOSP_DIVISION"].apply(
        lambda x: categorical_lookup["HOSP_DIVISION"][int(x) - 1]
    )

    table_df = table_df.groupby("HOSP_DIVISION").YEAR.value_counts().unstack(0)

    table_df.to_csv("results/table2.csv")
