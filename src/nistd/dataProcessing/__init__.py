import re
import pandas as pd


label_cols = ["DIED", "PROLONGED_LOS", "OR_RETURN"]
categorical_cols = [
    "SEX",
    "HOSP_LOCTEACH",
    "HOSP_REGION",
    "INCOME_QRTL",
    "PAY1",
    "RACE",
]

continuous_cols = ["LOS", "AGE"]

thyroidectomy_icd9 = [
    "0631",
    "0639",
    "064",
    "0650",
    "0651",
    "0652",
]

thyroidectomy_icd10 = [
    "0GTK0ZZ",
    "0GTK4ZZ",
    "0GTJ0ZZ",
    "0GTJ4ZZ",
    "0GTH0ZZ",
    "0GBH0ZZ",
    "0GTH4ZZ",
    "0GBH3ZZ",
    "0GTG0ZZ",
    "0GBG0ZZ",
    "0GTG4ZZ",
    "0GBG3ZZ",
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
    "HOSP_DIVISION": [
        "New England",
        "Middle Atlantic",
        "East North Central",
        "West North Central",
        "South Atlantic",
        "East South Central",
        "West South Central",
        "Mountain",
        "Pacific",
    ],
}
