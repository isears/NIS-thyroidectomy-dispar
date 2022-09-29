import statsmodels.formula.api as sm
import numpy as np
from numpy.linalg import LinAlgError
import pandas as pd
from scipy.stats import fisher_exact
from nistd.dataProcessing import get_dtypes, label_cols, categorical_cols, ProcClass
from nistd import logging


def lr_or(df: pd.DataFrame, pclass: str):
    """
    Use a logistic regression model to compute Odds Ratios
    """

    # TODO: move to more global util class?
    categoricals = [
        "SEX",
        "HOSP_LOCTEACH",
        "HOSP_REGION",
        "PAY1",
        "RACE",
    ]

    # only include if data actually available
    categoricals = [c for c in categoricals if c in df.columns]

    # if "PROCEDURE_TYPE" in df.columns:
    #     # categoricals = ["PROCEDURE_TYPE", "HOSP_LOCTEACH", "HOSP_REGION"]
    #     categoricals.append("PROCEDURE_TYPE")

    independent_vars = [c for c in df.columns if c not in label_cols]

    # Binarize the non-categorical variables
    if "INCOME_QRTL" in df.columns:
        df["INCOME_QRTL"] = df["INCOME_QRTL"] > 2

    if "AGE" in df.columns:
        df["AGE"] = df["AGE"] > 65

    if "APRDRG_Severity" in df.columns:
        df["APRDRG_Severity"] = df["APRDRG_Severity"] > 2

    if "APRDRG_Risk_Mortality" in df.columns:
        df["APRDRG_Risk_Mortality"] = df["APRDRG_Risk_Mortality"] > 2

    for c in categoricals:
        # Set the reference category for every category as the category with the largest # of samples
        reference_group = df[c].value_counts().index[0]
        independent_vars[
            independent_vars.index(c)
        ] = f"C({c}, Treatment(reference='{reference_group}'))"
        df[c] = df[c].astype("str")

    independent_vars = " + ".join(independent_vars)

    for outcome in label_cols:
        formula_str = f"{outcome} ~ " + independent_vars

        logging.info(f"Formula string: {formula_str}")
        lr = sm.logit(formula_str, data=df)

        try:
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

            print(table3)

            save_path = f"results/table3_{outcome}_{pclass}.csv"
            logging.info(f"Computation complete, saving to {save_path}")

            table3.to_csv(save_path)
        except LinAlgError as e:
            logging.warning(f"Singular matrix for outcome {outcome} ({pclass})")


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
    all_classes = list()

    for pclass in ProcClass:
        df = pd.read_csv(f"cache/preprocessed_{pclass.name}.csv")

        dfc = df.copy()

        if pclass == ProcClass.LAPAROSCOPIC:
            dfc["LAPAROSCOPIC"] = 1
        else:
            dfc["LAPAROSCOPIC"] = 0

        all_classes.append(dfc)

        lr_or(df, pclass.name)

    combined_df = pd.concat(all_classes)
    kept_columns = ["LAPAROSCOPIC", "HOSP_LOCTEACH", "HOSP_REGION"] + label_cols
    combined_df = combined_df[kept_columns]
    lr_or(combined_df, "combined")
