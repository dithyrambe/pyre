from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import pendulum
from pyre.tax_wrappers.av import AV
from pyre.tax_wrappers.base import Contribution, Withdrawal
from pyre.tax_wrappers.cto import CTO
from pyre.tax_wrappers.pea import PEA
from rich.progress import track

plt.style.use("ggplot")


AMOUNT = 60_000.0
PCT = 0.035
INVESTMENT_DURATION = pendulum.Duration(years=10)
START = pendulum.parse("2025-01-01")
END = START + INVESTMENT_DURATION
DEATH = pendulum.parse("2091-01-01")
ANNUALIZED_RETURN = 0.07
INFLATION = 0.03
ADJUSTED_ANNUALIZED_RETURN = ANNUALIZED_RETURN - INFLATION
INTERVAL = DEATH - START

data = {
    _: []
    for _ in [
        "date",
        "pea_value",
        "cto_value",
        "pea_net",
        "cto_net",
        "pea_tax",
        "cto_tax",
    ]
}

pea = PEA(
    fees=0.00,
    annualized_return=ADJUSTED_ANNUALIZED_RETURN,
    opening_date=pendulum.parse("2024-05-01"),
)  # type: ignore
cto = CTO(fees=0.00, annualized_return=ADJUSTED_ANNUALIZED_RETURN, opening_date=START)  # type: ignore

pea.contribute(Contribution(70_000, datetime=pendulum.parse("2024-12-01")))
cto.contribute(Contribution(40_000, datetime=pendulum.parse("2024-12-01")))


for dt in [*INTERVAL.range("years")]:
    contribution = Contribution(amount=AMOUNT, datetime=dt)
    withdrawal = Withdrawal(pct=PCT, datetime=dt.add(days=1))

    if dt <= END:
        if pea.total_contribution(dt) + contribution.amount < pea.CONTRIBUTION_LIMIT:
            pea.contribute(contribution=contribution)
        else:
            cto.contribute(contribution=contribution)

    pea_net, pea_tax = pea.withdraw(
        withdrawal=withdrawal, dry_run=dt <= pendulum.parse("2056-01-01")
    )
    cto_net, cto_tax = cto.withdraw(
        withdrawal=withdrawal, dry_run=dt <= pendulum.parse("2056-01-01")
    )

    data["date"].append(dt)
    data["pea_value"].append(pea.portfolio_value(dt))
    data["cto_value"].append(cto.portfolio_value(dt))
    data["pea_net"].append(pea_net)
    data["cto_net"].append(cto_net)
    data["pea_tax"].append(pea_tax)
    data["cto_tax"].append(cto_tax)

df = pd.DataFrame(data).set_index("date")
df["Rente pea+cto"] = (df["pea_net"] + df["cto_net"]) / 12
df["Taxe pea+cto"] = (df["pea_tax"] + df["cto_tax"]) / 12
df["Portfolio Value"] = df["pea_value"] + df["cto_value"]
value = pea.portfolio_value(END) + cto.portfolio_value(END)

fig, ax1 = plt.subplots()
(df[["Rente pea+cto", "Taxe pea+cto"]]).plot.area(
    ax=ax1,
    figsize=(15, 10),
    legend=True,
    title=f"DCA €{AMOUNT} / year for {INVESTMENT_DURATION.years} years",
    stacked=True,
    alpha=0.7,
    xlabel="Year",
    ylabel="€ / month",
)
plt.show()
