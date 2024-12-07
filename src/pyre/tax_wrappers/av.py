import pendulum

from pyre.tax_wrappers.base import TaxWrapper, Withdrawal
from pyre.tax_wrappers.constants import (
    ISR,
    PFU,
    PS,
)


class AV(TaxWrapper):
    TAX_MINIMAL_HOLDING_PERIOD = pendulum.Duration(years=8)
    TAX_RELIEF = 4_600.0
    PRELEVEMENT_FORFAITAIRE = PF = 0.075
    SOFT_CONTRIBUTION_LIMIT = 150_000

    def apply_taxation(self, withdrawal: Withdrawal) -> tuple[float, float]:
        total_contribution = self.total_contribution(withdrawal.datetime)
        portfolio_value = self.portfolio_value(withdrawal.datetime)
        gross_amount = self._get_gross_amount(withdrawal)
        gain = (
            self.gain(withdrawal.datetime) * gross_amount / portfolio_value
            if portfolio_value
            else 0
        )

        if (
            withdrawal.datetime >= (self.opening_date + self.TAX_MINIMAL_HOLDING_PERIOD)
            and total_contribution
        ):
            remaining_taxable = max(gain - self.TAX_RELIEF, 0)
            tax_ps = gain * PS
            tax_pf = (
                remaining_taxable
                * self.PF
                * min(total_contribution, self.SOFT_CONTRIBUTION_LIMIT)
                / total_contribution
            )
            tax_isr = (
                remaining_taxable
                * ISR
                * max(total_contribution - self.SOFT_CONTRIBUTION_LIMIT, 0)
                / total_contribution
            )
            tax = tax_ps + tax_pf + tax_isr
        else:
            tax = gain * PFU
        return gross_amount - tax, tax
