import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client
from datetime import datetime, timezone

# --- Page Config ---
st.set_page_config(
    page_title="SupplyChain Pro | Analytics Dashboard",
    page_icon="🚚",
    layout="wide"
)

# --- Theme Configuration ---
st.markdown("""
<style>
    /* Base styles */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .stMetric {
        background-color: var(--secondary-background-color);
        border-radius: 8px;
        padding: 15px;
        border: 1px solid var(--border-color);
    }
    
    h1 {
        color: var(--heading-color);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 10px;
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: var(--secondary-background-color);
        border-top: 1px solid var(--border-color);
    }
    
    .stFileUploader > div {
        background-color: var(--secondary-background-color) !important;
        border-color: var(--border-color) !important;
    }
    
    :root {
        --primary-color: #2a3f5f;
        --background-color: #f8f9fa;
        --secondary-background-color: white;
        --text-color: #31333F;
        --heading-color: #2a3f5f;
        --border-color: #e0e0e0;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #FAFAFA;
            --heading-color: #FAFAFA;
            --border-color: #444;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Supabase Setup ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- Header ---
st.title("Supply Chain Analytics Dashboard")
st.caption("Powered by Python + Supabase, by Sigi Castro")

# --- Generate CSV Template ---
def generate_template():
    dates = pd.date_range("2024-01-01", periods=10)
    delivery_dates = dates + pd.to_timedelta(np.random.randint(2, 10, 10), unit='d')
    promised_dates = dates + pd.to_timedelta(np.random.randint(3, 8, 10), unit='d')
    
    return pd.DataFrame({
        "Order_Date": dates.strftime("%Y-%m-%d"),
        "Delivery_Date": delivery_dates.strftime("%Y-%m-%d"),
        "Promised_Delivery_Date": promised_dates.strftime("%Y-%m-%d"),
        "Sales": np.random.randint(500, 5000, 10),
        "Average_Inventory": np.random.randint(200, 1000, 10)
    })

# --- CSV Validation ---
def validate_csv(df):
    required_columns = {
        "Order_Date": "datetime64[ns]",
        "Delivery_Date": "datetime64[ns]",
        "Promised_Delivery_Date": "datetime64[ns]",
        "Sales": "numeric",
        "Average_Inventory": "numeric"
    }
    
    errors = []
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing columns: {', '.join(missing_cols)}")
    
    for col, dtype in required_columns.items():
        if col in df.columns:
            if dtype == "datetime64[ns]":
                try:
                    pd.to_datetime(df[col])
                except:
                    errors.append(f"'{col}' must be dates (YYYY-MM-DD)")
            elif dtype == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"'{col}' must be numbers")
    
    return errors

# --- KPI Calculation ---
def calculate_kpis(df):
    try:
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        df['Delivery_Date'] = pd.to_datetime(df['Delivery_Date'])
        df['Promised_Delivery_Date'] = pd.to_datetime(df['Promised_Delivery_Date'])
        
        df['On_Time'] = df['Delivery_Date'] <= df['Promised_Delivery_Date']
        on_time_rate = df['On_Time'].mean()
        inventory_turnover = df['Sales'].sum() / df['Average_Inventory'].mean()
        
        return {
            "on_time_rate": on_time_rate,
            "inventory_turnover": inventory_turnover,
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

# --- Main UI ---
with st.expander("📌 How to use this dashboard", expanded=True):
    st.markdown("""
    1. **Download the template** below  
    2. Fill it with your supply chain data  
    3. Upload the CSV to see KPIs  
    """)

# --- File Upload + Template ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
with col2:
    st.download_button(
        label="Download CSV Template",
        data=generate_template().to_csv(index=False),
        file_name="supply_chain_template.csv",
        mime="text/csv",
        help="Guaranteed correct format"
    )

# --- Process Uploaded File ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    validation_errors = validate_csv(df)
    
    if validation_errors:
        st.error("❌ Invalid CSV format. Please fix these issues:")
        for error in validation_errors:
            st.write(f"- {error}")
        st.markdown("**Tip:** Use the template to avoid errors.")
    else:
        kpis = calculate_kpis(df)
        
        if kpis["error"]:
            st.error(f"Calculation error: {kpis['error']}")
        else:
            st.success("✅ Data processed successfully!")
            
            # --- Display KPIs ---
            tab1, tab2 = st.tabs(["Dashboard", "Raw Data"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("On-Time Delivery Rate", 
                             f"{kpis['on_time_rate']:.1%}",
                             help="Percentage of orders delivered by promised date")
                with col2:
                    st.metric("Inventory Turnover", 
                             round(kpis['inventory_turnover'], 2),
                             help="Sales / Average Inventory")
            
            with tab2:
                st.dataframe(df.head(1000))
            
            # --- Save to Database ---
            try:
                supabase.table("kpi_results").insert({
                    "on_time_rate": float(kpis["on_time_rate"]),
                    "inventory_turnover": float(kpis["inventory_turnover"]),
                    "timestamp": datetime.now(timezone.utc).isoformat()  # ISO format with timezone
                }).execute()
            except Exception as e:
                st.warning(f"⚠️ Could not save to database: {str(e)}")

# --- Portfolio Footer ---
st.markdown("""
<div class="footer">
    <a href="https://github.com/trussrod/datasig.io" target="_blank">View my portfolio</a>
</div>
""", unsafe_allow_html=True)