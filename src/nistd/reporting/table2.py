import pandas as pd
import numpy as np
from nistd.dataProcessing import label_cols, get_dtypes

if __name__ == "__main__":
    processed_df = pd.read_csv("cache/preprocessed.csv")
    filtered_df = pd.read_csv("cache/filtered.csv", dtype=get_dtypes())

    outcomes_df = processed_df[[c for c in processed_df.columns if c in label_cols]]

    all_n, all_percent = list(), list()

    for outcome_name in outcomes_df.columns:
        # Assuming all are binary
        assert outcomes_df[outcome_name].isin([0.0, 1.0]).all()

        n = outcomes_df[outcome_name].sum()
        percent = (n / len(outcomes_df)) * 100

        all_n.append(n)
        all_percent.append(percent)

    table2_df = pd.DataFrame(
        data={"N": all_n, "%": all_percent}, index=outcomes_df.columns
    )

    table2_df["N (%)"] = table2_df.apply(
        lambda row: f"{row['N']} ({row['%']:.2f})", axis=1
    )

    # Get age mean / sem
    age_mean = filtered_df["LOS"].mean()
    age_sem = filtered_df["LOS"].std() / np.sqrt(len(filtered_df))
    as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
    table2_df = pd.concat(
        [pd.DataFrame(data={"N (%)": as_str}, index=["LOS mean"]), table2_df]
    )

    table2_df.to_csv("results/table2.csv")
