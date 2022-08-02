"""
Apply study inclusion criteria:
- Age > 18
- Diagnosis codes of interest
- Procedure codes of interest
"""
import pandas as pd
from nistd import logging


class InclusionCriteria:
    def __init__(self, base_df) -> None:
        self.base_df = base_df
        logging.info(
            f"Inclusion criteria filter instantiated with n={len(self.base_df)}"
        )

    @staticmethod
    def _ic_over18(df_in: pd.DataFrame):
        return df_in[df_in["AGE"] > 18]

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
        
        return df


if __name__ == "__main__":
    ic = InclusionCriteria(pd.read_csv("cache/thyroidectomies.csv"))
    filtered = ic.apply_ic()
    filtered.to_csv("cache/filtered.csv", index=False)
