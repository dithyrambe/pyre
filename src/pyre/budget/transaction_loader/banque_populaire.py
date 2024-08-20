from pathlib import Path

import pandas as pd
import pendulum

from pyre.budget.transaction_loader import TransactionLoader


class BanquePopulaireLoader(TransactionLoader):
    SEP = ";"
    DECIMAL = ","
    ENCODING = "latin"

    def read_raw(self, path: str | Path) -> pd.DataFrame:
        return pd.read_csv(path, sep=self.SEP, decimal=self.DECIMAL, encoding=self.ENCODING)

    def get_event_date(self, df: pd.DataFrame) -> pd.Series:
        return df["Date de comptabilisation"].apply(
            lambda date: pendulum.from_format(date, fmt="DD/MM/YYYY").to_date_string()
        )

    def get_event_datetime(self, df: pd.DataFrame) -> pd.Series:
        return df["Date de comptabilisation"].apply(
            lambda date: pendulum.from_format(date, fmt="DD/MM/YYYY").to_iso8601_string()
        )

    def get_description(self, df: pd.DataFrame) -> pd.Series:
        return df["Libelle operation"].fillna(df["Libelle simplifie"])

    def get_amount(self, df: pd.DataFrame) -> pd.Series:
        return df["Debit"].fillna(df["Credit"])

    def get_category(self, df: pd.DataFrame) -> pd.Series:
        return df["Categorie"]

    def get_subcategory(self, df: pd.DataFrame) -> pd.Series:
        return df["Sous categorie"]
