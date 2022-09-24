import pandas as pd
import numpy as np
from nistd.dataProcessing import label_cols, categorical_cols, get_dtypes, ProcClass

if __name__ == "__main__":
    for pclass in ProcClass:
        processed_df = pd.read_csv(f"cache/preprocessed_{pclass.name}.csv")

        categoricals = processed_df[
            [c for c in processed_df.columns if c in categorical_cols]
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

        # Get age mean / sem
        age_mean = processed_df["AGE"].mean()
        age_sem = processed_df["AGE"].std() / np.sqrt(len(processed_df))
        as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
        table1_df = pd.concat(
            [pd.DataFrame(data={"N (%)": as_str}, index=["Age mean"]), table1_df]
        )

        table1_df.to_csv(f"results/table1_{pclass.name}.csv")
