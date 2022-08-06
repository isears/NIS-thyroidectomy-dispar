"""
Prepare raw (filtered) NIS data for use in models
"""
import pandas as pd
from nistd import logging
from nistd.dataProcessing import (
    thyroidectomy_codes,
    or_return_codes,
    get_proc_cols,
    get_dtypes,
)


def validate(df: pd.DataFrame) -> None:
    def assert_binary(column_name: str):
        assert df[column_name].isin([1.0, 0.0]).all()

    for column in df.columns:
        assert df[column].dtype == float, f"Found non-float column: {column}"

    # AGE
    assert df["AGE"].max() < 200
    assert df["AGE"].min() >= 18

    # FEMALE
    assert_binary("FEMALE")

    # RACE
    race_columns = [c for c in df.columns if c.startswith("RACE_")]
    assert len(race_columns) == 6
    for race_column in race_columns:
        assert_binary(race_column)

    # APRDRG
    for aprdrg in ["APRDRG_Severity", "APRDRG_Risk_Mortality"]:
        assert df[aprdrg].max() == 4
        assert df[aprdrg].min() == 0

    # Insurance status
    insurance_columns = [c for c in df.columns if c.startswith("PAY1_")]
    assert len(insurance_columns) == 6

    # Income
    assert_binary("INCOME_QRTL")

    # Hospital type
    hosp_type_columns = [c for c in df.columns if c.startswith("HOSP_LOCTEACH_")]
    assert len(hosp_type_columns) == 3
    for hosp_type_column in hosp_type_columns:
        assert_binary(hosp_type_column)

    # Hospital region
    hosp_region_columns = [c for c in df.columns if c.startswith("HOSP_REGION_")]
    assert len(hosp_region_columns) == 4
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

    copy_cols = ["AGE", "FEMALE", "APRDRG_Severity", "APRDRG_Risk_Mortality", "DIED"]
    for cc in copy_cols:
        df_out[cc] = df_in[cc]

    # One-hot encoded columns
    ohe_columns = ["PAY1", "RACE", "HOSP_LOCTEACH", "HOSP_REGION"]
    # If this fails, it's b/c we didn't drop na in inclusion criteria
    df_in[ohe_columns] = df_in[ohe_columns].astype("int")
    dumdums = pd.get_dummies(
        df_in[ohe_columns],
        columns=ohe_columns,
        prefix={
            "PAY1": "PAY1",
            "RACE": "RACE",
            "HOSP_LOCTEACH": "HOSP_LOCTEACH",
            "HOSP_REGION": "HOSP_REGION",
        },
        dummy_na=False,
        dtype=float,
    )
    df_out = pd.concat([df_out, dumdums], axis=1)

    df_out["INCOME_QRTL"] = df_in.apply(
        lambda row: row["ZIPINC_QRTL"] if row["ZIPINC_QRTL"] else row["ZIPINC"], axis=1
    )

    df_out["INCOME_QRTL"] = (df_out["INCOME_QRTL"] > 2).astype(float)

    # Either simply defined prolonged length of stay as LOS > 2 or
    # More than one day after procedure
    # df_out["PROLONGED_LOS"] = (df_in["LOS"] > 2).astype(float)
    proc_cols = get_proc_cols(df_in.columns)

    def is_los_prolonged(row):
        """
        Label length of stay as "prolonged" if hospital LOS is
        more than 1 day after the last thyroidectomy procedure
        """
        procs_only = row[proc_cols]
        proc_num = procs_only[procs_only.isin(thyroidectomy_codes)].index[-1]
        proc_num = proc_num[proc_num.index("PR") + 2 :]

        # In its infinite wisdom, the state of Ohio went from reporting a max of 9
        # procedures in 2013, to 110 in 2014
        assert int(proc_num) <= 110

        proc_day = row[f"PRDAY{proc_num}"]
        return float(row["LOS"] > proc_day + 1)

    df_out["PROLONGED_LOS"] = df_in.apply(is_los_prolonged, axis=1)

    # OR return
    def returned_to_OR(row):
        or_return = row[proc_cols].isin(or_return_codes).any()

        if or_return:
            procs_only = row[proc_cols]
            thyroidectomy_procnum = procs_only[
                procs_only.isin(thyroidectomy_codes)
            ].index[0]
            thyroidectomy_procnum = thyroidectomy_procnum[
                thyroidectomy_procnum.index("PR") + 2 :
            ]

            or_return_num = procs_only[procs_only.isin(or_return_codes)].index[0]
            or_return_num = or_return_num[or_return_num.index("PR") + 2 :]

            if int(thyroidectomy_procnum) > int(or_return_num):
                logging.warning("Detected OR return piror to thyroidectomy")

        return float(or_return)

    df_out["OR_RETURN"] = df_in.apply(returned_to_OR, axis=1)

    validate(df_out)
    df_out.to_csv("cache/preprocessed.csv", index=False)
