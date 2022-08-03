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
