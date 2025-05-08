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

# Sales and inventory (randomized)
sales = np.random.randint(500, 5000, num_records)
inventory = np.random.randint(200, 1000, num_records)

# Create DataFrame
df = pd.DataFrame({
    "Order_Date": [d.strftime("%Y-%m-%d") for d in order_dates],
    "Delivery_Date": [d.strftime("%Y-%m-%d") for d in delivery_dates],
    "Promised_Delivery_Date": [d.strftime("%Y-%m-%d") for d in promised_dates],
    "Sales": sales,
    "Average_Inventory": inventory
})

# Save to CSV
df.to_csv("supply_chain_data_1000.csv", index=False)
print("Generated supply_chain_data_1000.csv with 1,000 records!")