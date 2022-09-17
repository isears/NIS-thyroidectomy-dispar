"""
Prepare raw (filtered) NIS data for use in models
"""
import pandas as pd
from nistd import logging
from nistd.dataProcessing import (
    get_proc_cols,
    get_dtypes,
    label_cols,
    categorical_lookup,
)
import numpy as np


def validate(df: pd.DataFrame) -> None:
    def assert_binary(column_name: str):
        assert df[column_name].isin([1.0, 0.0]).all()

        ratio = df[column_name].sum() / len(df)
        if ratio > 0.99 or ratio < 0.01:
            logging.warning(f"High homogeneity in {column_name} ({ratio})")

    for column in df.columns:
        assert df[column].dtype == float, f"Found non-float column: {column}"
        assert not df[column].isna().any(), f"{column} has nans"
        assert not df[column].apply(lambda x: np.isinf(x)).any(), f"{column} has infs"

    # SEX
    sex_columns = [c for c in df.columns if c.startswith("SEX_")]
    for sex_column in sex_columns:
        assert_binary(sex_column)

    # RACE
    race_columns = [c for c in df.columns if c.startswith("RACE_")]
    for race_column in race_columns:
        assert_binary(race_column)

    # Hospital type
    hosp_type_columns = [c for c in df.columns if c.startswith("HOSP_LOCTEACH_")]
    for hosp_type_column in hosp_type_columns:
        assert_binary(hosp_type_column)

    # Hospital region
    hosp_region_columns = [c for c in df.columns if c.startswith("HOSP_REGION_")]
    for hosp_region_column in hosp_region_columns:
        assert_binary(hosp_region_column)

    ## Outcomes
    # LOS
    assert_binary("PROLONGED_LOS")

    # OR return
    assert_binary("OR_RETURN")

    # mortality
    assert_binary("DIED")


if __name__ == "__main__":
    # TODO: need to load ICD dx / proc columns as str, not float
    df_in = pd.read_csv("cache/filtered.csv", dtype=get_dtypes())
    df_out = pd.DataFrame()

    copy_cols = [
        "AGE",
        "APRDRG_Severity",
        "APRDRG_Risk_Mortality",
        "DIED",
        "PAY1",
        "RACE",
        "FEMALE",
        "HOSP_LOCTEACH",
        "HOSP_REGION",
    ]

    # FEMALE, RACE may have NAs
    df_in["FEMALE"] = df_in["FEMALE"].fillna(2)
    df_in["RACE"] = df_in["RACE"].fillna(7)

    for cc in copy_cols:
        df_out[cc] = df_in[cc].astype(int)

    df_out["INCOME_QRTL"] = df_in["ZIPINC_QRTL"].fillna(df_in["ZIPINC"])
    assert not df_out["INCOME_QRTL"].isna().any()
    df_out["INCOME_QRTL"] = df_out["INCOME_QRTL"].astype(int)

    proc_cols = get_proc_cols(df_in.columns)

    for key, lookup_table in categorical_lookup.items():
        # FEMALE is 0, 1, but all other columns don't have a 0 val
        if key == "FEMALE":
            df_out[key] = df_out[key].apply(lambda x: lookup_table[x])
        else:
            df_out[key] = df_out[key].apply(lambda x: lookup_table[x - 1])

    df_out = df_out.rename(columns={"FEMALE": "SEX"})

    df_out.to_csv("cache/preprocessed.csv", index=False)
