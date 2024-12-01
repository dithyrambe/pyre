from unittest.mock import patch

import pendulum
import pytest

from pyre.tax_wrappers.base import Withdrawal
from pyre.tax_wrappers.constants import ISR, PFU, PS
from pyre.tax_wrappers.av import AV


def test_av_before_min_holding():
    opening = pendulum.parse("2025-01-01")
    av = AV(opening_date=opening)

    with (
        patch.object(av, "total_contribution") as total_contribution,
        patch.object(av, "portfolio_value") as portfolio_value,
    ):
        total_contribution.return_value = 10_000
        portfolio_value.return_value = 15_000

        withdrawal = Withdrawal(
            pct=1.0, datetime=(opening + av.TAX_MINIMAL_HOLDING_PERIOD).subtract(days=1)
        )
        net, tax = av.withdraw(withdrawal=withdrawal)
        expected_tax = 5_000 * PFU
        expected_net = 15_000 - expected_tax
        assert tax == expected_tax
        assert net == expected_net


@pytest.mark.parametrize(
    argnames=("contribution", "gains", "expected_tax"),
    argvalues=[
        (10_000, 1_000, 1_000 * PS + max(0, 1_000 - AV.TAX_RELIEF) * AV.PF),
        (50_000, 10_000, 10_000 * PS + max(0, 10_000 - AV.TAX_RELIEF) * AV.PF),
        (
            200_000,
            40_000,
            40_000 * PS
            + max(0, 40_000 - AV.TAX_RELIEF)
            * (AV.PF * AV.SOFT_CONTRIBUTION_LIMIT + (200_000 - AV.SOFT_CONTRIBUTION_LIMIT) * ISR)
            / 200_000,
        ),
    ],
)
def test_pea_after_min_holding(contribution: float, gains: float, expected_tax: float):
    opening = pendulum.parse("2025-01-01")
    av = AV(opening_date=opening)

    with (
        patch.object(av, "total_contribution") as total_contribution,
        patch.object(av, "portfolio_value") as portfolio_value,
    ):
        total_contribution.return_value = contribution
        portfolio_value.return_value = contribution + gains

        withdrawal = Withdrawal(
            pct=1.0, datetime=(opening + av.TAX_MINIMAL_HOLDING_PERIOD).add(days=1)
        )
        _, tax = av.withdraw(withdrawal=withdrawal)
        assert tax == expected_tax
