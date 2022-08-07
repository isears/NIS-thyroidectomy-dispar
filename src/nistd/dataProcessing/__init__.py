import re
import pandas as pd


label_cols = ["DIED", "PROLONGED_LOS", "OR_RETURN"]

# Malignant neoplasm of thyroid gland
diagnosis_icd9 = ["193"]
diagnosis_icd10 = ["C73"]

diagnosis_codes = diagnosis_icd9 + diagnosis_icd10

thyroidectomy_icd9 = [
    "064",  # Complete thyroidectomy
    "0652",  # Complete substernal thyroidectomy
]
thyroidectomy_icd10 = [
    "0GTK0ZZ",  # Complete thyroidectomy (open)
    "0GTK4ZZ",  # Complete thyroidectomy (percutaneous)
]

thyroidectomy_codes = thyroidectomy_icd9 + thyroidectomy_icd10

# Control bleeding in neck
or_return_icd9 = ["3998"]
or_return_icd10 = ["0W360ZZ", "0W363ZZ", "0W364ZZ"]

or_return_codes = or_return_icd9 + or_return_icd10


def get_proc_cols(all_cols):
    icd9_proc_cols = [col for col in all_cols if re.search("^PR[0-9]{1,2}$", col)]
    icd10_proc_cols = [col for col in all_cols if re.search("^I10_PR[0-9]{1,2}$", col)]

    return icd9_proc_cols + icd10_proc_cols


def get_dx_cols(all_cols):
    icd9_cols = [col for col in all_cols if re.search("^DX[0-9]{1,2}$", col)]
    icd10_cols = [col for col in all_cols if re.search("^I10_DX[0-9]{1,2}$", col)]

    return icd9_cols + icd10_cols


def get_dtypes():
    return pd.read_csv("cache/dtypes.csv", index_col=0).squeeze("columns").to_dict()


# TODO
categorical_lookup = {
    "FEMALE": ["Male", "Female", "Unknown"],
    "RACE": [
        "White",
        "Black",
        "Hispanic",
        "Asian or Pacific Islander",
        "Native American",
        "Other",
        "Unknown",
    ],
    "PAY1": [
        "Medicare",
        "Medicaid",
        "Private insurance",
        "Self-pay",
        "No charge",
        "Other",
    ],
    "HOSP_LOCTEACH": ["Rural", "Urban nonteaching", "Urban teaching"],
    "HOSP_REGION": ["Northeast", "Midwest", "South", "West"],
}
