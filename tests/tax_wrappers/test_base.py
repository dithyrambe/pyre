import pytest
import pendulum

from pyre.tax_wrappers.base import Contribution, TaxWrapper, Withdrawal


class DummyTaxWrapper(TaxWrapper):
    def apply_taxation(self, withdrawal: Withdrawal) -> tuple[float, float]:
        return super().apply_taxation(withdrawal)


def test_withdrawal_persistence():
    contributions = [
        Contribution(1000, datetime=pendulum.parse("2024-01-01")),
        Contribution(1000, datetime=pendulum.parse("2024-02-01")),
    ]
    withdrawal = Withdrawal(datetime=pendulum.parse("2024-03-01"), amount=1000)
    tw = DummyTaxWrapper(annualized_return=0.1)
    for contribution in contributions:
        tw.contribute(contribution)
    tw.withdraw(withdrawal)

    rate = 1 + tw.monthly_return

    assert tw.portfolio_value(pendulum.parse("2023-12-01")) == 0
    assert tw.portfolio_value(pendulum.parse("2024-01-01")) == 1000
    assert tw.portfolio_value(pendulum.parse("2024-02-01")) == 1000 * rate + 1000
    assert tw.portfolio_value(pendulum.parse("2024-03-02")) == 1000 * rate**2 + 1000 * rate - 1000
    assert (
        tw.portfolio_value(pendulum.parse("2024-04-01"))
        == (1000 * rate**2 + 1000 * rate - 1000) * rate
    )


@pytest.mark.parametrize(
    ("contributions", "withdrawals", "date", "expected_residual_contribution"),
    [
        (
            [Contribution(100_000, pendulum.parse("2020-01-01"))],
            [],
            pendulum.parse("2020-01-01"),
            100_000,
        ),
        (
            [Contribution(100_000, pendulum.parse("2020-01-01"))],
            [Withdrawal(pendulum.parse("2021-01-01"), amount=10_000)],
            pendulum.parse("2021-01-02"),
            95_000,
        ),
        (
            [Contribution(100_000, pendulum.parse("2020-01-01"))],
            [
                Withdrawal(pendulum.parse("2021-01-01"), amount=10_000),
                Withdrawal(pendulum.parse("2022-01-01"), amount=10_000),
            ],
            pendulum.parse("2022-01-02"),
            95_000 - 10_000 * 95_000 / 380_000,
        ),
    ],
)
def test_residual_contribution(contributions, withdrawals, date, expected_residual_contribution):
    wrapper = DummyTaxWrapper(annualized_return=1.00)
    for contrib in contributions:
        wrapper.contribute(contrib)
    for withdrawal in withdrawals:
        wrapper.withdraw(withdrawal)

    residual_contribution = wrapper.residual_contribution(date)
    assert residual_contribution == expected_residual_contribution
