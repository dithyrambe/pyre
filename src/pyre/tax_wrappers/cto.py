import pendulum

from pyre.tax_wrappers.base import TaxWrapper, Withdrawal
from pyre.tax_wrappers.constants import PRELEVEMENT_FORFAITAIRE_UNIQUE


class CTO(TaxWrapper):
    def withdraw(self, withdrawal: Withdrawal) -> tuple[float, float]:
        tax_rate = PRELEVEMENT_FORFAITAIRE_UNIQUE
        portfolio_value = self.portfolio_value(withdrawal.datetime)

        gross_withdraw = withdrawal.pct * portfolio_value
        gain = self.gain(withdrawal.datetime) * withdrawal.pct
        tax = tax_rate * gain
        return gross_withdraw - tax, tax
