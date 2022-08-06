import pandas as pd
import numpy as np
from nistd.dataProcessing import label_cols, get_dtypes

if __name__ == "__main__":
    processed_df = pd.read_csv("cache/preprocessed.csv")
    filtered_df = pd.read_csv("cache/filtered.csv", dtype=get_dtypes())

    variables_df = processed_df[
        [c for c in processed_df.columns if c not in label_cols]
    ]

    all_n, all_percent = list(), list()

    for variable_name in variables_df.columns:
        # Assuming all are binary
        assert variables_df[variable_name].isin([0.0, 1.0]).all()

        n = variables_df[variable_name].sum()
        percent = (n / len(variables_df)) * 100

        all_n.append(n)
        all_percent.append(percent)

    table1_df = pd.DataFrame(
        data={"N": all_n, "%": all_percent}, index=variables_df.columns
    )

    table1_df["N (%)"] = table1_df.apply(
        lambda row: f"{row['N']} ({row['%']:.2f})", axis=1
    )

    # Get age mean / sem
    age_mean = filtered_df["AGE"].mean()
    age_sem = filtered_df["AGE"].std() / np.sqrt(len(filtered_df))
    as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
    table1_df = pd.concat(
        [pd.DataFrame(data={"N (%)": as_str}, index=["Age mean"]), table1_df]
    )

    table1_df.to_csv("results/table1.csv")
