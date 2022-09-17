import re
import pandas as pd
import importlib.resources as pkg_resources
from nistd import icdcodes
from enum import Enum, auto


label_cols = ["DIED", "PROLONGED_LOS", "ANASTOMOTIC_LEAK", "INFECTION"]
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

# Anastomotic leak
anastomotic_leak_codes = [
    "56981",
    "56722",
    "99749",
    "99859",
    "5695",
    "K632",
    "K651",
    "K9189",
    "K6811",
    "K630",
]

# Infection
infection_codes = [
    "99859",
    "99592",
    "78552",
    "56721",
    "56729",
    "5679",
    "T814XXA",
    "T814",
    "T8140XA",
    "T8141XA",
    "T8142XA",
    "T8143XA",
    "T8144XA",
    "T8149XA",
    "R6520",
    "R6521",
    "K650",
    "K659",
]


class ProcClass(Enum):
    OPEN = auto()
    LAPAROSCOPIC = auto()

    def getProcCodes(self):
        return pkg_resources.read_text(icdcodes, f"proc_{self.name}.txt").split()

    def getAnastomosisCodes(self):
        return pkg_resources.read_text(icdcodes, f"anastomosis_{self.name}.txt").split()


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
