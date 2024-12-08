from decimal import DivisionByZero
from typing import Any

import pandas as pd


class AllPickedException(Exception):
    """Raised when no more sample available to pick in data"""


class Labeler:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.already_picked = []

    def pick(self) -> dict[str, Any]:
        eligible = self.data[~self.data["id"].isin(self.already_picked)]
        if eligible.empty:
            raise AllPickedException("All samples have already been picked")
        sample = eligible.sample(1).iloc[0].to_dict()
        self.already_picked.append(sample["id"])
        return sample
