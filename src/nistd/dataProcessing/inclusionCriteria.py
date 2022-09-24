"""
Apply study inclusion criteria:
- Age > 18
- Diagnosis codes of interest
- Procedure codes of interest
"""
import pandas as pd
from nistd import logging
from nistd.dataProcessing import get_dtypes, ProcClass, get_proc_cols


class InclusionCriteria:
    def __init__(self, base_df: pd.DataFrame, pclass: ProcClass) -> None:
        self.base_df = base_df
        self.pclass = pclass
        logging.info(
            f"Inclusion criteria filter instantiated with n={len(self.base_df)} ({self.pclass.name})"
        )

    @staticmethod
    def _ic_dropna(df_in: pd.DataFrame) -> pd.DataFrame:
        # We can handle FEMALE and RACE missing, but need other columns
        cols = [
            "AGE",
            "PAY1",
            "APRDRG_Severity",
            "APRDRG_Risk_Mortality",
            "HOSP_LOCTEACH",
            "HOSP_REGION",
            "DIED",
            "LOS",
        ]

        df_in = df_in.dropna(subset=cols, how="any")

        # Can have either ZIPINC OR ZIPINC_QRTL
        df_in = df_in.dropna(subset=["ZIPINC", "ZIPINC_QRTL"], how="all")

        return df_in

    @staticmethod
    def _ic_age(df_in: pd.DataFrame) -> pd.DataFrame:
        return df_in[df_in["AGE"] >= 18]

    def _ic_prefix(self, df_in: pd.DataFrame) -> pd.DataFrame:
        # Assume that if the original procedure was laparoscopic, the anastomosis was as well
        proc_codes = self.pclass.getProcCodes() + self.pclass.getProcOnlyCodes()
        return df_in[
            df_in[get_proc_cols(df_in.columns)].isin(proc_codes).any(axis="columns")
        ]

    def apply_ic(self) -> pd.DataFrame:
        ic_methods = [m for m in dir(self) if m.startswith("_ic")]
        df = self.base_df

        for method_name in ic_methods:
            before_count = len(df)
            func = getattr(self, method_name)
            df = func(df)
            after_count = len(df)
            logging.info(
                f"{method_name} diff: {before_count - after_count} ({before_count} -> {after_count})"
            )

        logging.info(f"Success, final size: {len(df)}")
        return df


if __name__ == "__main__":

    for pclass in ProcClass:
        df = pd.read_parquet("cache/rectalcancer.parquet")
        ic = InclusionCriteria(df, pclass)
        filtered = ic.apply_ic()
        filtered.to_parquet(f"cache/filtered_{pclass.name}.parquet")
