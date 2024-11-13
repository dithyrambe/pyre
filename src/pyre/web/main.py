from uuid import uuid4
from tempfile import NamedTemporaryFile
from nicegui import ui
from datetime import datetime
import pendulum
import pandas as pd
import matplotlib.pyplot as plt
from pyre.tax_wrappers.av import AV
from pyre.tax_wrappers.cto import CTO
from pyre.tax_wrappers.pea import PEA
from pyre.tax_wrappers.base import Contribution, Withdrawal
from pyre.web.utils.dates import date_input

# Initialize global constants
CONSTANTS = {
    "duration": 20,
    "amount": 3000.0,
    "pct": 0.035,
    "start": pendulum.parse("2024-11-01"),
    "annualized_return": 0.075,
}

tax_wrappers = {}



with ui.grid(columns="auto 1fr").classes("w-full h-full"):
    with ui.column().classes("w-full"):
        with ui.row().classes("w-full"):
            amount_input = ui.number("Monthly savings", value=3000.0).bind_value_to(CONSTANTS, "amount")
            duration_input = ui.number("Duration", value=20).bind_value_to(CONSTANTS, "duration")
        WRAPPERS_COL = ui.column()
    GRAPH_CARD = ui.card().classes("no-shadow")

def add_tax_wrapper_card():
    wrapper_data = {
        "id": str(uuid4()),
        "type": "PEA",
        "priority": 1,
        "fees": None,
        "annualized_return": None,
        "opening_date": None,
    }

    with ui.expansion(f"Wrapper {len(tax_wrappers) + 1} (PEA)", value=True) as expansion, ui.card() as wrapper_card:
        wrapper_type = ui.toggle(["PEA", "AV", "CTO"], value="PEA", on_change=lambda e: expansion.set_text(f"Wrapper {len(tax_wrappers) + 1} ({e.value})")).bind_value_to(wrapper_data, "type")
        fees_input = ui.number("Fees", value=0.00).bind_value_to(wrapper_data, "fees")
        return_input = ui.number("Annualized Return", value=CONSTANTS["annualized_return"]).bind_value_to(wrapper_data, "annualized_return")
        opening_date_input = date_input("Opening date", default=pendulum.today().to_date_string()).bind_value_to(wrapper_data, "opening_date")

        def create_wrapper():
            wrapper_type_val = wrapper_type.value
            fees = float(fees_input.value)
            annualized_return = float(return_input.value)
            opening_date = pendulum.parse(str(opening_date_input.value))

            if wrapper_type_val == "PEA":
                wrapper = PEA(fees=fees, annualized_return=annualized_return, opening_date=opening_date)
            elif wrapper_type_val == "CTO":
                wrapper = CTO(fees=fees, annualized_return=annualized_return, opening_date=opening_date)
            elif wrapper_type_val == "AV":
                wrapper = AV(fees=fees, annualized_return=annualized_return, opening_date=opening_date)
            else:
                raise ValueError()

            # Add to global tax wrappers list
            tax_wrappers[wrapper_data["id"]] = wrapper
            ui.notify(f"Added {wrapper_type_val}")
            expansion.value = False

        ui.button("Create / Update", on_click=create_wrapper)
    wrapper_card.move(expansion)
    expansion.move(WRAPPERS_COL)

# Function to simulate and update the chart
def run_simulation():
    # Clear data for a fresh simulation
    wrappers = iter(tax_wrappers.values())
    wrapper = next(wrappers)
    simulation_data = {"date": [], **{_id: [] for _id, _ in tax_wrappers.items()}}

    # Simulate over each month in the investment period
    end_date = CONSTANTS["start"].add(years=int(CONSTANTS["duration"]))
    interval = end_date - CONSTANTS["start"]

    for dt in interval.range("months"):
        contribution = Contribution(amount=CONSTANTS["amount"], datetime=dt)
        withdrawal = Withdrawal(pct=CONSTANTS["pct"], datetime=dt)

        nets, taxes = [0 for _ in tax_wrappers], [0 for _ in tax_wrappers]
        if wrapper.total_contribution(dt) + contribution.amount > wrapper.CONTRIBUTION_LIMIT:
            wrapper = next(wrappers)
        wrapper.contribute(contribution=contribution)
        for _id, values in simulation_data.items():
            if _id  == "date":
                values.append(dt)
                continue
            w = tax_wrappers[_id]
            net, tax = w.withdraw(withdrawal=withdrawal)
            values.append(net)

    # Generate the DataFrame for plotting
    df = pd.DataFrame(simulation_data).set_index("date")

    echart = ui.echart({
        "xAxis": {"type": "category", "data": [dt.to_date_string() for dt in simulation_data["date"]]},
        "yAxis": {"type": "value"},
        "legend": {"textStyle": {"color": "gray"}},
        "series": [
            {"type": "line", "name": f"{n}-{tax_wrappers[_id].__class__.__name__}", "data": [round(_) for _ in values], "stack": "Total", "emphasis": {"focus": "series"}, "areaStyle": {}}
            for n, (_id, values) in enumerate(simulation_data.items()) if _id != "date"
        ],
        "tooltip": {
            "trigger": 'axis',
            "axisPointer": {
              "type": 'cross',
            },
          },
    }).classes("w-full")
    echart.move(GRAPH_CARD)
    echart.classes("h-full")

# Set up the main UI
add_tax_wrapper_card()
ui.button("+", on_click=add_tax_wrapper_card)
ui.button("Run Simulation", on_click=run_simulation)

ui.dark_mode(True)
ui.run()
