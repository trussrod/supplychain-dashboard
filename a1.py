import pandas as pd

def calculate_kpis(df):
    df['Delivery_Time'] = pd.to_datetime(df['Delivery_Date']) - pd.to_datetime(df['Order_Date'])
    df['On_Time_Rate'] = (df['Delivery_Time'] <= df['Promised_Time']).mean()
    inventory_turnover = df['Sales'] / df['Average_Inventory']
    return {
        'On_Time_Delivery_Rate': df['On_Time_Rate'],
        'Inventory_Turnover': inventory_turnover
    }