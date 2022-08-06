import pandas as pd
from nistd.dataProcessing import label_cols

if __name__ == "__main__":
    df = pd.read_csv("cache/preprocessed.csv")

    variables_df = df[[c for c in df.columns if c not in label_cols]]
    outcomes_df = df[[c for c in df.columns if c in label_cols]]

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

    table1_df.to_csv("results/table1.csv")
