import pandas as pd
import numpy as np

def preprocess_data(df):
    """
    Preprocess the raw price dataframe.
    - Parse dates.
    - Handle missing values using interpolation.
    - Handle outliers (cap them based on IQR or simple thresholds).
    - Rename columns for Prophet (ds, y).
    """
    if df.empty:
        return df
        
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date').reset_index(drop=True)
    
    # Handle Missing Values
    # We will interpolate missing numerical values (Price_Rs_kg)
    df['Price_Rs_kg'] = df['Price_Rs_kg'].interpolate(method='linear')
    df['Price_Rs_kg'] = df['Price_Rs_kg'].bfill().ffill() # edge cases
    
    # Simple Outlier Handling using IQR
    Q1 = df['Price_Rs_kg'].quantile(0.25)
    Q3 = df['Price_Rs_kg'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df['Price_Rs_kg'] = np.where(
        df['Price_Rs_kg'] > upper_bound, upper_bound,
        np.where(df['Price_Rs_kg'] < lower_bound, lower_bound, df['Price_Rs_kg'])
    )
    
    # Ensure multi-factor columns exist (for real API Fallbacks)
    for col in ['Rainfall_mm', 'Export_Demand_Index', 'USD_INR_Rate', 'Is_Harvest_Season']:
        if col not in df.columns:
            # Provide sensible defaults if missing from a real scraper
            if col == 'Rainfall_mm': df[col] = 10.0
            elif col == 'Export_Demand_Index': df[col] = 75.0
            elif col == 'USD_INR_Rate': df[col] = 83.5
            elif col == 'Is_Harvest_Season': df[col] = 0
            
        # Handle NA in regressors
        df[col] = df[col].interpolate(method='linear').bfill().ffill()
    
    # Rename for Prophet
    prophet_df = pd.DataFrame({
        'ds': df['Date'],
        'y': df['Price_Rs_kg'],
        'Rainfall_mm': df['Rainfall_mm'],
        'Export_Demand_Index': df['Export_Demand_Index'],
        'USD_INR_Rate': df['USD_INR_Rate'],
        'Is_Harvest_Season': df['Is_Harvest_Season']
    })
    
    return prophet_df

def merge_datasets(cardamom_df, pepper_df):
    """
    If we ever need a unified dataset for multi-variate analysis.
    For now, Prophet univariate uses them separately, but we provide this for the pipeline requirement.
    """
    # Merge on Date
    merged = pd.merge(cardamom_df, pepper_df, on='Date', how='outer', suffixes=('_cardamom', '_pepper'))
    merged = merged.sort_values(by='Date').reset_index(drop=True)
    return merged
