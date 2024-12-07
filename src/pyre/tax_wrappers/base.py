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
    datetime: DateTime
    amount: float | None = None
    pct: float | None = None

    def __post_init__(self):
        if self.amount is None and self.pct is None:
            raise ValueError("Either amount or pct must be specified.")


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
        self.withdrawals: list[Withdrawal] = []

    def total_contribution(self, datetime: DateTime):
        return sum(
            _.amount
            for _ in filter(lambda contrib: contrib.datetime <= datetime, self.contributions)
        )

    def portfolio_value(self, datetime: DateTime):
        months_since_contributions = [
            (datetime - contrib.datetime).in_months() for contrib in self.contributions
        ]
        months_since_withdrawals = [
            (datetime - withdrawal.datetime).in_months() for withdrawal in self.withdrawals
        ]
        compounded_contributions = [
            contrib.amount * (1 + self.monthly_return) ** months
            for contrib, months in zip(self.contributions, months_since_contributions)
            if months >= 0
        ]
        compounded_withdrawals = [
            withdrawal.amount * (1 + self.monthly_return) ** months
            for withdrawal, months in zip(self.withdrawals, months_since_withdrawals)
            if months >= 0
        ]
        return sum(compounded_contributions) - sum(compounded_withdrawals)

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

    def withdraw(self, withdrawal: Withdrawal, dry_run: bool = False) -> tuple[float, float]:
        if not dry_run:
            datetime = withdrawal.datetime
            amount = withdrawal.amount or withdrawal.pct * self.portfolio_value(withdrawal.datetime)
            self.withdrawals.append(Withdrawal(datetime=datetime, amount=amount))
        net_amount, tax_amount = self.apply_taxation(withdrawal)
        return net_amount, tax_amount

    def _get_gross_amount(self, withdrawal: Withdrawal) -> float:
        gross_withdraw = withdrawal.amount
        if withdrawal.pct:
            gross_withdraw = withdrawal.pct * self.portfolio_value(withdrawal.datetime)
        return gross_withdraw

    @abstractmethod
    def apply_taxation(self, withdrawal: Withdrawal) -> tuple[float, float]:
        gross_amount = self._get_gross_amount(withdrawal)
        return gross_amount, 0.0
