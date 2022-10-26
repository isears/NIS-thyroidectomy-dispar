import statsmodels.formula.api as sm
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from nistd.dataProcessing import label_cols
from nistd import logging

import docx
from docx.shared import Inches


def lr_or(df: pd.DataFrame):
    """
    Use a logistic regression model to compute Odds Ratios
    """

    # TODO: move to more global util class?
    categoricals = [
        "SEX",
        "HOSP_LOCTEACH",
        # "HOSP_DIVISION",
        # "HOSP_REGION",
        # "INCOME_QRTL",
        "PAY1",
        "RACE",
        # "APRDRG_Severity",
        # "APRDRG_Risk_Mortality",
    ]

    independent_vars = [
        c for c in df.columns if c not in label_cols and c != "HOSP_REGION"
    ]

    # Binarize the non-categorical variables
    df["INCOME_QRTL"] = df["INCOME_QRTL"] > 2
    df["AGE"] = df["AGE"] > 65
    df["APRDRG_Severity"] = df["APRDRG_Severity"] > 2
    df["APRDRG_Risk_Mortality"] = df["APRDRG_Risk_Mortality"] > 2

    for c in categoricals:
        # Set the reference category for every category as the category with the largest # of samples
        # TODO: for one vs. rest odds ratios may just have to do several LR models, one for each category group
        reference_group = df[c].value_counts().index[0]
        independent_vars[
            independent_vars.index(c)
        ] = f"C({c}, Treatment(reference='{reference_group}'))"
        df[c] = df[c].astype("str")

    independent_vars = " + ".join(independent_vars)

    doc = docx.Document()
    table_doc = doc.add_table(rows=1, cols=1)
    table_doc.autofit = True
    table_doc.allow_autofit = True

    for outcome_idx, outcome in enumerate(label_cols):
        formula_str = f"{outcome} ~ " + independent_vars

        logging.info(f"Formula string: {formula_str}")
        lr = sm.logit(formula_str, data=df)
        res = lr.fit_regularized()

        odds_ratios = np.exp(res.params)
        lower_ci = np.exp(res.conf_int()[0])
        upper_ci = np.exp(res.conf_int()[1])

        def unwrap_pnames(param_name: str):
            try:
                ref = param_name.split("'")[1]
                var = param_name[param_name.index("T.") + 2 : -1]

                return f"{var} (compared to: {ref})"
            except IndexError:
                return param_name

        table3 = pd.DataFrame(
            data={
                "Odds Ratios": odds_ratios,
                "Lower CI": lower_ci,
                "Upper CI": upper_ci,
                "P Value": res.pvalues,
            },
            index=res.params.index,  # .map(unwrap_pnames),
        )

        table3.index = table3.index.map(unwrap_pnames)
        table3 = table3.drop(index="Intercept")

        # TODO: Every class has one group that doesn't appear in params b/c it's the reference class
        # Need to do a better job of selecting this
        # https://stackoverflow.com/questions/22431503/specifying-which-category-to-treat-as-the-base-with-statsmodels
        print(table3)

        save_path = f"results/table4_{outcome}.csv"
        logging.info(f"Computation complete, saving to {save_path}")

        table3.to_csv(save_path)

        col_cells = table_doc.add_column(Inches(2)).cells
        col_cells[0].text = outcome

        def add_single_row(row):
            if row["P Value"] < 0.01:
                p_value = "< 0.01"
            else:
                p_value = f"{row['P Value']:.2f}"

            formatted_str = f"{row['Odds Ratios']:.2f} ({row['Lower CI']:.2f}, {row['Upper CI']:.2f}); {p_value}"

            row_headers = [x.text for x in table_doc.column_cells(0)]

            if not row.name in row_headers:
                curr_row = table_doc.add_row().cells
                curr_row[0].text = row.name
            else:
                curr_row = table_doc.row_cells(row_headers.index(row.name))

            curr_row[outcome_idx + 1].text = formatted_str

        table3.apply(add_single_row, axis=1)

    table_doc.style = "Medium Grid 3 Accent 1"

    # Set width to be reasonable
    for row in table_doc.rows:
        for cell in row.cells:
            cell.width = Inches(2)

    doc.save(f"results/table4.docx")


if __name__ == "__main__":
    df = pd.read_csv("cache/preprocessed.csv")
    lr_or(df)
