import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import docx

from nistd.dataProcessing import categorical_lookup


if __name__ == "__main__":
    filtered_df = pd.read_parquet("cache/filtered.parquet")
    table_df = filtered_df[["YEAR", "HOSP_REGION"]]
    table_df["HOSP_REGION"] = table_df["HOSP_REGION"].apply(
        lambda x: categorical_lookup["HOSP_REGION"][int(x) - 1]
    )

    table_df = table_df.groupby("HOSP_REGION").YEAR.value_counts().unstack(0)

    table_df.to_csv("results/table2.csv")

    doc = docx.Document()
    table_doc = doc.add_table(rows=1, cols=len(table_df.columns) + 1)
    header_row = table_doc.row_cells(0)
    header_row[0].text = "Year"

    for ridx, region in enumerate(table_df.columns):
        header_row[ridx + 1].text = region

    def add_row(year):
        row = table_doc.add_row().cells
        row[0].text = str(year.name)

        for ridx, region in enumerate(table_df.columns):
            row[ridx + 1].text = f"{year[region]:,}"

    table_df.apply(add_row, axis=1)

    table_doc.style = "Medium Grid 3 Accent 1"

    doc.save(f"results/table2.docx")
