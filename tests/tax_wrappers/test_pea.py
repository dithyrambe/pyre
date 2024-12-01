from unittest.mock import patch

import pendulum

from pyre.tax_wrappers.base import Withdrawal
from pyre.tax_wrappers.constants import PFU, PS
from pyre.tax_wrappers.pea import PEA


def test_pea_before_min_holding():
    opening = pendulum.parse("2025-01-01")
    pea = PEA(opening_date=opening)

    with (
        patch.object(pea, "total_contribution") as total_contribution,
        patch.object(pea, "portfolio_value") as portfolio_value,
    ):
        total_contribution.return_value = 10_000
        portfolio_value.return_value = 15_000

        withdrawal = Withdrawal(
            pct=1.0, datetime=(opening + pea.TAX_MINIMAL_HOLDING_PERIOD).subtract(years=1)
        )
        net, tax = pea.withdraw(withdrawal=withdrawal)
        expected_tax = 5_000 * PFU
        expected_net = 15_000 - expected_tax
        assert tax == expected_tax
        assert net == expected_net


def test_pea_after_min_holding():
    opening = pendulum.parse("2025-01-01")
    pea = PEA(opening_date=opening)

    with (
        patch.object(pea, "total_contribution") as total_contribution,
        patch.object(pea, "portfolio_value") as portfolio_value,
    ):
        total_contribution.return_value = 10_000
        portfolio_value.return_value = 15_000

        withdrawal = Withdrawal(
            pct=1.0, datetime=(opening + pea.TAX_MINIMAL_HOLDING_PERIOD).add(years=1)
        )
        net, tax = pea.withdraw(withdrawal=withdrawal)
        expected_tax = 5_000 * PS
        expected_net = 15_000 - expected_tax
        assert tax == expected_tax
        assert net == expected_net
