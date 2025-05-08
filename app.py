import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- SETUP SUPABASE (FREE CLOUD DATABASE) --- #
url = "https://bznvxydkjonkqzzkidqf.supabase.co"  # Replace in Step 4
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6bnZ4eWRram9ua3F6emtpZHFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3MzgxNjEsImV4cCI6MjA2MjMxNDE2MX0.6W4SutQW4uh5a_4GLmV04rjv87VD5Mj7WuBPm8XtVIQ"  # Replace in Step 4
supabase = create_client(url, key)

# --- CALCULATE KPIs --- #
def calculate_kpis(df):
    # Convert dates to datetime
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Delivery_Date'] = pd.to_datetime(df['Delivery_Date'])
    
    # Calculate On-Time Delivery Rate
    df['On_Time'] = df['Delivery_Date'] <= df['Promised_Delivery_Date']
    on_time_rate = df['On_Time'].mean()
    
    # Calculate Inventory Turnover
    inventory_turnover = df['Sales'].sum() / df['Average_Inventory'].mean()
    
    return {
        "on_time_rate": on_time_rate,
        "inventory_turnover": inventory_turnover
    }

# --- STREAMLIT APP --- #
st.title("📊 Supply Chain KPI Dashboard")
uploaded_file = st.file_uploader("Upload your supply chain data (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    kpis = calculate_kpis(df)
    
    st.success("✅ Data processed successfully!")
    st.write("## Key Metrics")
    
    # Display KPIs
    col1, col2 = st.columns(2)
    with col1:
        st.metric("On-Time Delivery Rate", f"{kpis['on_time_rate']:.1%}")
    with col2:
        st.metric("Inventory Turnover", round(kpis['inventory_turnover'], 2))
    
    # Save to Supabase (optional)
    supabase.table("kpi_results").insert({
        "on_time_rate": kpis['on_time_rate'],
        "inventory_turnover": kpis['inventory_turnover']
    }).execute()