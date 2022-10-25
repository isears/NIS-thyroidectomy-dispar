"""
Prepare raw (filtered) NIS data for use in models
"""
import pandas as pd
from nistd import logging
from nistd.dataProcessing import (
    thyroidectomy_codes,
    or_return_codes,
    get_proc_cols,
    label_cols,
    categorical_lookup,
)
import numpy as np


if __name__ == "__main__":
    # TODO: need to load ICD dx / proc columns as str, not float
    df_in = pd.read_parquet("cache/filtered.parquet")
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
        "HOSP_DIVISION",
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
        return int(row["LOS"] > proc_day + 1)

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
                logging.warning("Detected OR return prior to thyroidectomy")

        return int(or_return)

    df_out["OR_RETURN"] = df_in.apply(returned_to_OR, axis=1)

    for key, lookup_table in categorical_lookup.items():
        # FEMALE is 0, 1, but all other columns don't have a 0 val
        if key == "FEMALE":
            df_out[key] = df_out[key].apply(lambda x: lookup_table[x])
        else:
            df_out[key] = df_out[key].apply(lambda x: lookup_table[x - 1])

    df_out = df_out.rename(columns={"FEMALE": "SEX"})

    df_out.to_csv("cache/preprocessed.csv", index=False)
