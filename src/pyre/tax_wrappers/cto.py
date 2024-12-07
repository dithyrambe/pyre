import pendulum

from pyre.tax_wrappers.base import TaxWrapper, Withdrawal
from pyre.tax_wrappers.constants import PRELEVEMENT_FORFAITAIRE_UNIQUE


class CTO(TaxWrapper):
    TAX_MINIMAL_HOLDING_PERIOD = pendulum.Duration(years=5)

    def withdraw(self, withdrawal: Withdrawal) -> tuple[float, float]:
        tax_rate = PRELEVEMENT_FORFAITAIRE_UNIQUE
        portfolio_value = self.portfolio_value(withdrawal.datetime)
        gain_ratio = self.gain(withdrawal.datetime) / portfolio_value if portfolio_value else 0.0

        gross_amount = self._get_gross_amount(withdrawal)
        gain = gross_amount * gain_ratio
        tax = tax_rate * gain
        return gross_amount - tax, tax
