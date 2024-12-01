from abc import ABC, abstractmethod
from dataclasses import dataclass

from pendulum import DateTime
import numpy as np
import pendulum


@dataclass
class Contribution:
    amount: float
    datetime: DateTime


@dataclass
class Withdrawal:
    pct: float
    datetime: DateTime


class TaxWrapper(ABC):
    CONTRIBUTION_LIMIT = np.inf

    def __init__(
        self,
        fees: float = 0.0,
        annualized_return: float = 0.0,
        opening_date: DateTime | None = None,
    ) -> None:
        self.opening_date = opening_date or pendulum.now()
        self.fees = fees
        self.annualized_return = annualized_return - self.fees
        self.monthly_return = (1 + self.annualized_return) ** (1 / 12) - 1
        self.contributions: list[Contribution] = []

    def total_contribution(self, datetime: DateTime):
        return sum(
            _.amount
            for _ in filter(lambda contrib: contrib.datetime <= datetime, self.contributions)
        )

    def portfolio_value(self, datetime: DateTime):
        months_since_contributions = [
            (datetime - contrib.datetime).in_months() for contrib in self.contributions
        ]
        compounded_contributions = [
            contrib.amount * (1 + self.monthly_return) ** months
            for contrib, months in zip(self.contributions, months_since_contributions)
            if months >= 0
        ]
        return sum(compounded_contributions)

    def gain(self, datetime: DateTime) -> float:
        return self.portfolio_value(datetime) - self.total_contribution(datetime)

    def contribute(self, contribution: Contribution) -> None:
        if self.contributions and self.contributions[-1].datetime > contribution.datetime:
            raise ValueError("Contribution is prior to last contribution")
        if (
            self.total_contribution(contribution.datetime) + contribution.amount
            > self.CONTRIBUTION_LIMIT
        ):
            raise ValueError(f"Contribution limit is {self.CONTRIBUTION_LIMIT}")
        self.contributions.append(contribution)

    @abstractmethod
    def withdraw(self, withdrawal: Withdrawal) -> tuple[float, float]:
        gross_withdraw = withdrawal.pct * self.portfolio_value(withdrawal.datetime)
        return gross_withdraw, 0.0
