from unittest.mock import patch

import pendulum

from pyre.tax_wrappers.base import Withdrawal
from pyre.tax_wrappers.constants import PFU
from pyre.tax_wrappers.cto import CTO


def test_cto():
    opening = pendulum.parse("2025-01-01")
    cto = CTO(opening_date=opening)

    with (
        patch.object(cto, "total_contribution") as total_contribution,
        patch.object(cto, "portfolio_value") as portfolio_value
    ):
        total_contribution.return_value = 10_000
        portfolio_value.return_value = 15_000

        withdrawal = Withdrawal(pct=1.0, datetime=(opening + cto.TAX_MINIMAL_HOLDING_PERIOD).subtract(years=1))
        net, tax = cto.withdraw(withdrawal=withdrawal)
        expected_tax = 5_000 * PFU
        expected_net = 15_000 - expected_tax
        assert tax == expected_tax
        assert net == expected_net
