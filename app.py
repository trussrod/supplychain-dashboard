import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
from pathlib import Path
import dataset  # Simple ORM for SQLite

# --- Page Config ---
st.set_page_config(
    page_title="SupplyChain Pro | Analytics Dashboard",
    page_icon="🚚",
    layout="wide"
)

# --- Theme CSS ---
st.markdown("""
<style>
    :root {
        --primary-color: #2a3f5f;
        --background-color: #f8f9fa;
        --secondary-background-color: white;
        --text-color: #31333F;
        --border-color: #e0e0e0;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--background-color);
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .stMetric {
        background-color: var(--secondary-background-color);
        border-radius: 8px;
        padding: 15px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    h1 {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 10px;
    }
    
    .stFileUploader > div {
        background-color: var(--secondary-background-color) !important;
        border-color: var(--border-color) !important;
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
        z-index: 100;
    }
    
    /* Force dark mode compatibility */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #FAFAFA;
            --border-color: #444;
        }
        
        /* Fix for Streamlit components */
        .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak {
            background-color: var(--background-color) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Database Setup ---
DB_PATH = Path("supplychain.db")

@st.cache_resource
def init_db():
    """Initialize SQLite database with dataset ORM"""
    db = dataset.connect(f"sqlite:///{DB_PATH}")
    
    # Create table if not exists
    db.query("""
    CREATE TABLE IF NOT EXISTS kpi_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        on_time_rate REAL,
        inventory_turnover REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    return db

def save_kpis(kpis):
    """Save KPIs to SQLite database"""
    db = init_db()
    db["kpi_results"].insert({
        "on_time_rate": float(kpis["on_time_rate"]),
        "inventory_turnover": float(kpis["inventory_turnover"])
    })

# --- Data Processing Functions ---
def generate_template():
    """Generate valid CSV template"""
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
    """Validate uploaded CSV structure"""
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
    """Calculate core supply chain metrics"""
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
            "error": None,
            "df": df  # Return processed dataframe
        }
    except Exception as e:
        return {"error": str(e)}

# --- UI Components ---
st.title("📊 Supply Chain Analytics Dashboard")
st.caption("Now with SQLite database | No more dependency conflicts")

with st.expander("📌 How to use", expanded=True):
    st.markdown("""
    1. **Download template**  
    2. Fill with your data  
    3. Upload CSV to analyze  
    """)

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
with col2:
    if st.download_button(
        label="Download Template",
        data=generate_template().to_csv(index=False),
        file_name="supply_chain_template.csv",
        mime="text/csv"
    ):
        st.toast("Template downloaded!", icon="✅")

# --- Main Processing ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    validation_errors = validate_csv(df)
    
    if validation_errors:
        st.error("❌ Invalid CSV format:")
        for error in validation_errors:
            st.write(f"- {error}")
    else:
        kpis = calculate_kpis(df)
        
        if kpis["error"]:
            st.error(f"Calculation error: {kpis['error']}")
        else:
            st.success("✅ Data processed successfully!")
            processed_df = kpis["df"]
            
            # --- Tabs Layout ---
            tab1, tab2, tab3 = st.tabs(["📈 KPIs", "🚢 Shipping Lanes", "📋 Raw Data"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "On-Time Delivery Rate", 
                        f"{kpis['on_time_rate']:.1%}",
                        help="Percentage delivered by promised date"
                    )
                with col2:
                    st.metric(
                        "Inventory Turnover", 
                        f"{kpis['inventory_turnover']:.2f}",
                        help="Sales / Average Inventory"
                    )
                
                # Weekly Trends
                st.markdown("### Weekly Performance")
                weekly_data = processed_df.set_index('Order_Date').resample('W').agg({
                    'On_Time': 'mean',
                    'Sales': 'sum'
                }).reset_index()
                
                fig = px.line(
                    weekly_data,
                    x='Order_Date',
                    y=['On_Time', 'Sales'],
                    labels={'value': 'Metric'},
                    height=400
                )
                fig.update_yaxes(tickformat=".0%", secondary_y=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Sankey Diagram
                st.markdown("### Shipping Lane Performance")
                processed_df['Lane'] = "Lane_" + (processed_df.groupby(['Order_Date']).cumcount() % 3 + 1).astype(str)
                lane_perf = processed_df.groupby(['Lane', 'On_Time']).size().reset_index(name='Count')
                
                all_nodes = list(lane_perf['Lane'].unique()) + ['On Time', 'Delayed']
                source = [all_nodes.index(x) for x in lane_perf['Lane']]
                target = [all_nodes.index('On Time' if x else 'Delayed') for x in lane_perf['On_Time']]
                
                fig = go.Figure(go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=all_nodes,
                        color=["#4CAF50" if "Lane" in x else "#FFC107" if x == "On Time" else "#F44336" 
                               for x in all_nodes]
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=lane_perf['Count'],
                        color=["rgba(76, 175, 80, 0.3)" if x else "rgba(244, 67, 54, 0.3)" 
                               for x in lane_perf['On_Time']]
                    )
                ))
                fig.update_layout(height=500, margin=dict(l=50, r=50, b=50, t=50))
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.dataframe(processed_df, height=600, use_container_width=True)
            
            # Save to SQLite
            try:
                save_kpis(kpis)
                st.toast("Data saved to database!", icon="💾")
            except Exception as e:
                st.warning(f"⚠️ Database save failed: {str(e)}")

# --- Footer ---
st.markdown("""
<div class="footer">
    <a href="https://github.com/trussrod/datasig.io" target="_blank">View my portfolio</a>
</div>
""", unsafe_allow_html=True)