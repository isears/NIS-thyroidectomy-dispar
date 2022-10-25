import pandas as pd
import numpy as np
from nistd.dataProcessing import categorical_lookup

if __name__ == "__main__":
    processed_df = pd.read_csv("cache/preprocessed.csv")

    categoricals = processed_df[
        [c for c in processed_df.columns if c in categorical_lookup]
    ]

    all_n, all_percent = list(), list()
    table1_df = pd.DataFrame()

    for variable_name in categoricals.columns:
        vc = categoricals[variable_name].value_counts()

        def format_n(n):
            percent = n / len(processed_df) * 100
            return f"{n} ({percent:.2f})"

        table1_df = table1_df.append(
            pd.DataFrame(
                data={"N (%)": vc.apply(format_n).values},
                index=vc.index.map(lambda x: f"[{vc.name}] {x}"),
            )
        )

    # Get APDRG stats
    for aprdrg_col in ["APRDRG_Severity", "APRDRG_Risk_Mortality"]:
        over2_count = (processed_df[aprdrg_col] > 2).sum()
        as_str = f"{over2_count} ({100 * over2_count / len(processed_df):.2f})"
        table1_df = pd.concat(
            [
                pd.DataFrame(data={"N (%)": as_str}, index=[f"{aprdrg_col} > 2"]),
                table1_df,
            ]
        )

    # Get > 65
    over65_count = (processed_df["AGE"] > 65).sum()
    as_str = f"{over65_count} ({100 * over65_count / len(processed_df):.2f})"
    table1_df = pd.concat(
        [pd.DataFrame(data={"N (%)": as_str}, index=["AGE > 65"]), table1_df]
    )

    # Get age mean / sem
    age_mean = processed_df["AGE"].mean()
    age_sem = processed_df["AGE"].std() / np.sqrt(len(processed_df))
    as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
    table1_df = pd.concat(
        [pd.DataFrame(data={"N (%)": as_str}, index=["Age mean"]), table1_df]
    )

    table1_df.to_csv("results/table1.csv")
