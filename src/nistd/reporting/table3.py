import pandas as pd
import numpy as np
import docx

from nistd.dataProcessing import label_cols
from nistd.reporting.table1 import make_cell_bold

if __name__ == "__main__":
    processed_df = pd.read_csv("cache/preprocessed.csv")
    filtered_df = pd.read_parquet("cache/filtered.parquet")

    outcomes_df = processed_df[[c for c in processed_df.columns if c in label_cols]]

    # Make docx
    doc = docx.Document()
    table_doc = doc.add_table(rows=1, cols=2)
    table_doc.autofit = True
    table_doc.allow_autofit = True

    header_row = table_doc.row_cells(0)
    header_row[0].text = "Outcome"
    header_row[1].text = "N (%)"
    make_cell_bold(header_row[0])
    make_cell_bold(header_row[1])

    all_n, all_percent = list(), list()

    for outcome_name in outcomes_df.columns:
        # Assuming all are binary
        assert outcomes_df[outcome_name].isin([0.0, 1.0]).all()

        n = outcomes_df[outcome_name].sum()
        percent = (n / len(outcomes_df)) * 100

        all_n.append(n)
        all_percent.append(percent)

        row = table_doc.add_row().cells
        row[0].text = outcome_name
        make_cell_bold(row[0])
        row[1].text = f"{n:,} ({percent:.2f})"

    table2_df = pd.DataFrame(
        data={"N": all_n, "%": all_percent}, index=outcomes_df.columns
    )

    table2_df["N (%)"] = table2_df.apply(
        lambda row: f"{row['N']} ({row['%']:.2f})", axis=1
    )

    # Get los mean / sem
    age_mean = filtered_df["LOS"].mean()
    age_sem = filtered_df["LOS"].std() / np.sqrt(len(filtered_df))
    as_str = f"{age_mean:.2f} +/- {age_sem:.2f}"
    table2_df = pd.concat(
        [pd.DataFrame(data={"N (%)": as_str}, index=["LOS mean"]), table2_df]
    )

    row = table_doc.add_row().cells
    row[0].text = "LOS"
    make_cell_bold(row[0])
    row[1].text = as_str

    table2_df = table2_df.drop(columns=["N", "%"])
    table2_df.to_csv("results/table3.csv")

    table_doc.style = "Table Grid"

    doc.save(f"results/table3.docx")
