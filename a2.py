import streamlit as st
import pandas as pd

st.title("Supply Chain KPI Generator")
uploaded_file = st.file_uploader("Upload your CSV file")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    kpis = calculate_kpis(df)
    st.write("## Key Metrics")
    st.metric("On-Time Delivery Rate", f"{kpis['On_Time_Rate']:.2%}")
    st.metric("Inventory Turnover", round(kpis['Inventory_Turnover'], 2))