import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone

# --- Page Config (MUST BE FIRST) ---
st.set_page_config(
    page_title="SupplyChain Pro | Analytics Dashboard",
    page_icon="🚚",
    layout="wide"
)

# --- Theme CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .stMetric { 
        background-color: white; 
        border-radius: 8px; 
        padding: 15px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
    }
    h1 { 
        color: #2a3f5f; 
        border-bottom: 2px solid #2a3f5f; 
        padding-bottom: 10px; 
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: white;
        border-top: 1px solid #e0e0e0;
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
st.caption("Powered by Python + Supabase")

# --- Data Processing Functions ---
def generate_template():
    dates = pd.date_range("2024-01-01", periods=10)
    delivery_dates = dates + pd.to_timedelta(np.random.randint(2, 10, 10), unit='d')
    promised_dates = dates + pd.to_timedelta(np.random.randint(1, 8, 10), unit='d')
    
    return pd.DataFrame({
        "Order_Date": dates.strftime("%Y-%m-%d"),
        "Delivery_Date": delivery_dates.strftime("%Y-%m-%d"),
        "Promised_Delivery_Date": promised_dates.strftime("%Y-%m-%d"),
        "Sales": np.random.randint(500, 5000, 10),
        "Average_Inventory": np.random.randint(200, 1000, 10)
    })

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

# --- File Upload Section ---
with st.expander("📌 How to use this dashboard", expanded=True):
    st.markdown("""
    1. **Download the template**  
    2. Fill it with your supply chain data  
    3. Upload the CSV to see KPIs  
    """)

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

# --- Main Dashboard ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    validation_errors = validate_csv(df)
    
    if validation_errors:
        st.error("❌ Invalid CSV format. Please fix these issues:")
        for error in validation_errors:
            st.write(f"- {error}")
    else:
        kpis = calculate_kpis(df)
        
        if kpis["error"]:
            st.error(f"Calculation error: {kpis['error']}")
        else:
            st.success("✅ Data processed successfully!")
            
            # --- KPI Cards ---
            tab1, tab2, tab3 = st.tabs(["Dashboard", "Shipping Lanes", "Raw Data"])
            
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
            
            # --- NEW: Sankey Diagram ---
            with tab2:
                st.markdown("### Shipping Lane Performance")
                
                # Create mock lanes (replace with real 'Origin'/'Destination' if available)
                df['Lane'] = "Lane_" + (df.groupby(['Order_Date']).cumcount() % 3 + 1).astype(str)
                
                # Group data
                lane_perf = df.groupby(['Lane', 'On_Time']).size().reset_index(name='Count')
                
                # Prepare nodes (lanes + statuses)
                all_nodes = list(lane_perf['Lane'].unique()) + ['On Time', 'Delayed']
                source = [all_nodes.index(x) for x in lane_perf['Lane']]
                target = [all_nodes.index('On Time' if x else 'Delayed') for x in lane_perf['On_Time']]
                value = lane_perf['Count']
                
                # Color coding
                node_colors = ["#4CAF50" if "Lane" in x else "#FFC107" if x == "On Time" else "#F44336" 
                              for x in all_nodes]
                link_colors = ["rgba(76, 175, 80, 0.3)" if x else "rgba(244, 67, 54, 0.3)" 
                              for x in lane_perf['On_Time']]
                
                # Build diagram
                fig = go.Figure(go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=all_nodes,
                        color=node_colors
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=value,
                        color=link_colors
                    )
                ))
                
                fig.update_layout(
                    height=500,
                    margin=dict(l=50, r=50, b=50, t=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 Shows distribution of on-time vs delayed deliveries per shipping lane")
            
            with tab3:
                st.dataframe(df.head(1000))
            
            # --- Database Save ---
            try:
                supabase.table("kpi_results").insert({
                    "on_time_rate": float(kpis["on_time_rate"]),
                    "inventory_turnover": float(kpis["inventory_turnover"]),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }).execute()
            except Exception as e:
                st.warning(f"⚠️ Could not save to database: {str(e)}")

# --- Footer ---
st.markdown("""
<div class="footer">
    <a href="https://github.com/trussrod/datasig.io" target="_blank">View my portfolio</a>
</div>
""", unsafe_allow_html=True)