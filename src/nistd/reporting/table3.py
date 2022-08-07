import statsmodels.formula.api as sm
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from nistd.dataProcessing import get_dtypes, label_cols
from nistd import logging


def lr_or(df: pd.DataFrame):
    """
    Use a logistic regression model to compute Odds Ratios
    """
    # TODO: move to more global util class?
    categoricals = [
        "SEX",
        "HOSP_LOCTEACH",
        "HOSP_REGION",
        "INCOME_QRTL",
        "PAY1",
        "RACE",
    ]

    independent_vars = [c for c in df.columns if c not in label_cols]

    for c in categoricals:
        independent_vars[independent_vars.index(c)] = f"C({c})"

    independent_vars = " + ".join(independent_vars)

    for outcome in label_cols:
        formula_str = f"{outcome} ~ " + independent_vars

        logging.info(f"Formula string: {formula_str}")
        lr = sm.logit(formula_str, data=df)
        res = lr.fit_regularized()

        odds_ratios = np.exp(res.params)
        lower_ci = np.exp(res.conf_int()[0])
        upper_ci = np.exp(res.conf_int()[1])

        table3 = pd.DataFrame(
            data={
                "Odds Ratios": odds_ratios,
                "Lower CI": lower_ci,
                "Upper CI": upper_ci,
                "P Value": res.pvalues,
            },
            index=res.params.index,
        )

        print(table3)

        save_path = f"results/table3_{outcome}.csv"
        logging.info(f"Computation complete, saving to {save_path}")

        table3.to_csv(save_path)


def lr_manual(df: pd.DataFrame):
    """
    Manually compute odds ratios
    """
    variables_df = df[[c for c in df.columns if c not in label_cols]]
    outcomes_df = df[[c for c in df.columns if c in label_cols]]

    for outcome_name in outcomes_df.columns:
        logging.info(f"Computing ORs for {outcome_name}")
        ors, pvals, lower_cis, upper_cis = list(), list(), list(), list()

        for variable_name in variables_df.columns:

            ct = pd.crosstab(variables_df[variable_name], outcomes_df[outcome_name])

            # If ony part of the 2x2 is 0, we can't compute odds ratios
            if 0 in ct.values or ct.shape != (2, 2):
                logging.warning(f"{variable_name} had 0s in crosstab")
                odds, p_value, lower_ci, upper_ci = [np.nan] * 4
            else:

                odds, p_value = fisher_exact(ct)
                z_confidence = 1.96
                root = np.sqrt(sum([1 / x for x in ct.values.flatten()]))
                base = np.log(odds)
                lower_ci, upper_ci = (
                    np.exp(base - z_confidence * root),
                    np.exp(base + z_confidence * root),
                )

            ors.append(odds)
            pvals.append(p_value)
            lower_cis.append(lower_ci)
            upper_cis.append(upper_ci)

        results_df = pd.DataFrame(
            data={
                "Odds Ratio": ors,
                "Lower CI": lower_cis,
                "Upper CI": upper_cis,
                "P Value": pvals,
            }
        )

        results_df.index = variables_df.columns
        save_path = f"results/table3_{outcome_name}.csv"
        logging.info(f"Computation complete, saving to {save_path}")

        results_df.to_csv(save_path)


if __name__ == "__main__":
    df = pd.read_csv("cache/preprocessed.csv")
    lr_or(df)
