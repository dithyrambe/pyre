import pendulum

from pyre.tax_wrappers.base import TaxWrapper, Withdrawal
from pyre.tax_wrappers.constants import PRELEVEMENT_FORFAITAIRE_UNIQUE, PRELEVEMENT_SOCIAUX


class PEA(TaxWrapper):
    CONTRIBUTION_LIMIT = 150_000.0
    TAX_MINIMAL_HOLDING_PERIOD = pendulum.Duration(years=5)

    def withdraw(self, withdrawal: Withdrawal) -> tuple[float, float]:
        tax_rate = PRELEVEMENT_FORFAITAIRE_UNIQUE
        if withdrawal.datetime >= (self.opening_date + self.TAX_MINIMAL_HOLDING_PERIOD):
            tax_rate = PRELEVEMENT_SOCIAUX
        portfolio_value = self.portfolio_value(withdrawal.datetime)

        gross_withdraw = withdrawal.pct * portfolio_value
        gain = self.gain(withdrawal.datetime) * withdrawal.pct
        tax = tax_rate * gain
        return gross_withdraw - tax, tax
