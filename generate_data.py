import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 1,000 rows of supply chain data
np.random.seed(42)
num_records = 1000

# Random dates (Jan 1 - Dec 31, 2024)
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

order_dates = [start_date + timedelta(days=np.random.randint(date_range)) for _ in range(num_records)]
delivery_days = np.random.randint(2, 10, num_records)  # Delivery takes 2-9 days
delivery_dates = [order_date + timedelta(days=int(delivery_day)) for order_date, delivery_day in zip(order_dates, delivery_days)]
promised_days = delivery_days + np.random.randint(-1, 2, num_records)  # Promised date is +/-1 day of actual
promised_dates = [order_date + timedelta(days=max(1, int(promised_day))) for order_date, promised_day in zip(order_dates, promised_days)]
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_supply_chain_data(num_records=1000, start_date="2024-01-01", end_date="2024-12-31"):
    """
    Generates realistic supply chain data with:
    - Order dates
    - Delivery dates (with realistic delays)
    - Promised delivery dates
    - Sales amounts
    - Inventory levels
    
    Parameters:
    - num_records: Number of rows to generate (default: 1000)
    - start_date: First order date (default: 2024-01-01)
    - end_date: Last order date (default: 2024-12-31)
    """
    np.random.seed(42)  # For reproducible results
    
    # Date range setup
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    date_range = (end_date - start_date).days
    
    # Generate order dates
    order_dates = [start_date + timedelta(days=np.random.randint(date_range)) 
                  for _ in range(num_records)]
    
    # Generate delivery timelines
    delivery_delays = np.random.randint(2, 15, num_records)  # 2-14 day delivery window
    promise_delays = delivery_delays - np.random.randint(0, 3, num_records)  # Promised dates are slightly optimistic
    
    delivery_dates = [order_date + timedelta(days=int(delay)) 
                     for order_date, delay in zip(order_dates, delivery_delays)]
    promised_dates = [order_date + timedelta(days=int(promise)) 
                     for order_date, promise in zip(order_dates, promise_delays)]
    
    # Generate sales and inventory data with realistic relationships
    base_sales = np.random.normal(5000, 1500, num_records).clip(500, 15000)  # Normal distribution clipped to reasonable range
    inventory = (base_sales / np.random.uniform(2, 8, num_records)).astype(int)  # Inventory turns between 2-8x
    
    # Create DataFrame
    df = pd.DataFrame({
        "Order_Date": [d.strftime("%Y-%m-%d") for d in order_dates],
        "Delivery_Date": [d.strftime("%Y-%m-%d") for d in delivery_dates],
        "Promised_Delivery_Date": [d.strftime("%Y-%m-%d") for d in promised_dates],
        "Sales": base_sales.round(2),
        "Average_Inventory": inventory
    })
    
    # Add some missing/erroneous data for realism
    mask = np.random.rand(num_records) < 0.02  # 2% chance of issues
    df.loc[mask, "Delivery_Date"] = np.nan
    df.loc[mask, "Sales"] *= 10  # Some outlier sales values
    
    return df

def save_data(df, filename="supply_chain_data.csv"):
    """Saves generated data to CSV"""
    df.to_csv(filename, index=False)
    print(f"✅ Generated {len(df)} records in '{filename}'")
    print("Columns:", df.columns.tolist())

if __name__ == "__main__":
    # Generate and save data
    data = generate_supply_chain_data(num_records=1000)
    save_data(data)
    
    # Sample output validation
    print("\nSample Data:")
    print(data.head())
    print(f"\nOn-Time Delivery Rate: {(pd.to_datetime(data['Delivery_Date']) <= pd.to_datetime(data['Promised_Delivery_Date'])).mean():.1%}")
    print(f"Inventory Turnover: {data['Sales'].sum() / data['Average_Inventory'].mean():.2f}")