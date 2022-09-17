import re
import pandas as pd
import importlib.resources as pkg_resources
from nistd import icdcodes


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

# Malignant neoplasm of rectum / rectosigmoid junction
diagnosis_icd9 = ["1541", "154"]
diagnosis_icd10 = ["C20", "C19"]

diagnosis_codes = diagnosis_icd9 + diagnosis_icd10

proc_open = ["4869", "4852", "4861", "4862", "4863", "4864", "0DTP0ZZ"]
proc_lap = [
    "4859",
    "4851",
    "0DTP4ZZ",
    "0DTP7ZZ",
    "0DTP8ZZ",
    "0DBP3ZZ",
    "0DBP4ZZ",
    "0DBP8ZZ",
]

proc_codes = proc_open + proc_lap

# Anastomosis
anastomosis_open = pkg_resources.read_text(icdcodes, "anastomosis_open.txt").split()
anastomosis_lap = pkg_resources.read_text(icdcodes, "anastomosis_lap.txt").split()
anastomosis_codes = anastomosis_open + anastomosis_lap


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
