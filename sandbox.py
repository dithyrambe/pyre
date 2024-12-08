import matplotlib.pyplot as plt
import pandas as pd
import pendulum
from pyre.tax_wrappers.av import AV
from pyre.tax_wrappers.base import Contribution, Withdrawal
from pyre.tax_wrappers.cto import CTO
from pyre.tax_wrappers.pea import PEA
from rich.progress import track

plt.style.use("ggplot")


AMOUNT = 10_000.0
PCT = 0.035
INVESTMENT_DURATION = pendulum.Duration(years=15)
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
        "pea_net",
        "cto_net",
        "pea_tax",
        "cto_tax",
    ]
}

pea = PEA(fees=0.003, annualized_return=ADJUSTED_ANNUALIZED_RETURN, opening_date=START)  # type: ignore
cto = CTO(fees=0.003, annualized_return=ADJUSTED_ANNUALIZED_RETURN, opening_date=START)  # type: ignore

for dt in track([*INTERVAL.range("years")]):
    contribution = Contribution(amount=AMOUNT, datetime=dt)
    withdrawal = Withdrawal(pct=PCT, datetime=dt)

    if dt <= END:
        if pea.total_contribution(dt) + contribution.amount < pea.CONTRIBUTION_LIMIT:
            pea.contribute(contribution=contribution)
        else:
            cto.contribute(contribution=contribution)

    pea_net, pea_tax = pea.withdraw(withdrawal=withdrawal, dry_run=dt <= END)
    cto_net, cto_tax = cto.withdraw(withdrawal=withdrawal, dry_run=dt <= END)

    data["date"].append(dt)
    data["pea_net"].append(pea_net)
    data["cto_net"].append(cto_net)
    data["pea_tax"].append(pea_tax)
    data["cto_tax"].append(cto_tax)

df = pd.DataFrame(data).set_index("date")
df["Rente pea+cto"] = df["pea_net"] + df["cto_net"]
df["Taxe pea+cto"] = df["pea_tax"] + df["cto_tax"]

ax = (df[["Rente pea+cto", "Taxe pea+cto"]]).plot.area(
    figsize=(15, 10),
    legend=True,
    title=f"DCA €{AMOUNT} / month for {INVESTMENT_DURATION.years} years",
    stacked=True,
    alpha=0.7,
)
plt.show()
plt.savefig("/tmp/fig.png", format="png")
