import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from nistd.dataProcessing import categorical_lookup


if __name__ == "__main__":
    filtered_df = pd.read_parquet("cache/filtered.parquet")
    table_df = filtered_df[["YEAR", "HOSP_REGION"]]
    table_df["HOSP_REGION"] = table_df["HOSP_REGION"].apply(
        lambda x: categorical_lookup["HOSP_REGION"][int(x) - 1]
    )

    table_df = table_df.groupby("HOSP_REGION").YEAR.value_counts().unstack(0)

    table_df.to_csv("results/table2.csv")
