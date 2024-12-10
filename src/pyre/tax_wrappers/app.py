from dataclasses import dataclass, field
from typing import Any

from pendulum import DateTime
import pendulum
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.state import session_state

from pyre.tax_wrappers.base import TaxWrapper

DATE_FMT = "YYYY-MM-DD"


def init_state(key: str, value: Any):
    if key not in st.session_state:
        setattr(st.session_state, key, value)


init_state("wrappers", [])
init_state("forms", [])


@dataclass
class Configuration:
    dca_amount: float
    yearly_withdrawal: float
    investment_duration: int
    start: DateTime
    end: DateTime
    death: DateTime
    annualized_return: float
    inflation: float


@dataclass
class TaxWrapperForm:
    opening_date: DateTime = field(
        default_factory=lambda: st.date_input(
            "Opening date", format=DATE_FMT, key=f"od_{len(st.session_state.forms)}"
        )
    )
    fees: float = field(
        default_factory=lambda: st.number_input(
            "Fees", value=3.0, format="%0.1f", step=0.1, key=f"fees_{len(st.session_state.forms)}"
        )
        / 100.0,
    )


def add_wrapper(wrapper):
    st.session_state.wrappers.append(wrapper)


def add_form(form):
    st.session_state.forms.append(form)


if st.button("Add tax wrapper"):
    form_id = f"{len(st.session_state.forms)}"
    with st.form(key=f"form_{form_id}") as form:
        tw = TaxWrapperForm()
        submit = st.form_submit_button(label="Add / Update")
    add_form(form)


def run_simulation():
    print(conf)


with st.sidebar:
    conf = Configuration(
        dca_amount=st.number_input("Amount €", value=500.0, format="%0.0f", step=100.0),
        yearly_withdrawal=(
            st.number_input("Yearly withdrawal %", value=3.5, format="%0.1f", step=0.1) / 100.0
        ),
        investment_duration=int(st.number_input("Investment duration", value=20, step=1)),
        start=st.date_input("Start date", format=DATE_FMT),
        end=st.date_input("End date", format=DATE_FMT),
        death=st.date_input("Death", format=DATE_FMT),
        annualized_return=(
            st.number_input("Annualized return", value=7.0, format="%0.1f", step=0.1) / 100.0
        ),
        inflation=st.number_input("Inflation", value=3.0, format="%0.1f", step=0.1) / 100.0,
    )
    run_sim = st.button("Run", on_click=run_simulation, type="primary", use_container_width=True)
