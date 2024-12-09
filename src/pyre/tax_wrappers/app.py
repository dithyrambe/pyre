import streamlit as st

# Using "with" notation
with st.sidebar:
    dca_amount = st.number_input("Amount €", value=500.0, format="%0.0f", step=100.0)
    yearly_withdrawal = (
        st.number_input("Yearly withdrawal %", value=3.5, format="%0.1f", step=0.1) / 100.0
    )
    investment_duration = int(st.number_input("Investment duration", value=20, step=1))
    start = st.date_input("Start date", format="YYYY-MM-DD")
    end = st.date_input("End date", format="YYYY-MM-DD")
