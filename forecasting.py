from prophet import Prophet
import pandas as pd

def train_and_forecast(df, periods=30):
    """
    Trains a Prophet model on the given dataset and forecasts the next 'periods' days.
    """
    if df.empty or len(df) < 10:
        return pd.DataFrame() # Not enough data
        
    m = Prophet(daily_seasonality=True, yearly_seasonality=True)
    
    # Add external multi-factor regressors
    regressors = ['Rainfall_mm', 'Export_Demand_Index', 'USD_INR_Rate', 'Is_Harvest_Season']
    for reg in regressors:
        if reg in df.columns:
            m.add_regressor(reg)
            
    m.fit(df)
    
    future = m.make_future_dataframe(periods=periods)
    
    # Populate future dataframe with external regressor projections
    if 'Rainfall_mm' in df.columns:
        # In a real system, these would be pulled from weather APIs or macro-economic forecasts
        # For this system, we project the last known values forward to simulate stable future conditions
        last_known = df.iloc[-1]
        for reg in regressors:
            if reg in df.columns:
                # Copy historical values where available
                future[reg] = df[reg]
                # Forward fill the 30 future days with the latest known value
                future[reg] = future[reg].ffill().fillna(last_known[reg])
                
    forecast = m.predict(future)
    
    return forecast

def analyze_best_selling_window(forecast_df, future_days=30):
    """
    Extracts the best time to SELL (highest price) for FARMERS 
    within the forecasted window.
    """
    if forecast_df.empty:
        return {"error": "No forecast data generated"}
        
    # Get only the future predictions
    future_forecast = forecast_df.tail(future_days).copy()
    future_forecast['ds'] = pd.to_datetime(future_forecast['ds'])
    
    # Find the day with the MAX forecasted price (yhat)
    max_row = future_forecast.loc[future_forecast['yhat'].idxmax()]
    
    best_date = max_row['ds'].strftime('%Y-%m-%d')
    expected_price = float(max_row['yhat'])
    lower_bound = float(max_row['yhat_lower'])
    upper_bound = float(max_row['yhat_upper'])
    
    return {
        "recommended_date": best_date,
        "expected_price_rs_kg": round(expected_price, 2),
        "confidence_interval": {
            "lower": round(lower_bound, 2),
            "upper": round(upper_bound, 2)
        },
        "message": f"Optimal selling window for maximum profit is around {best_date} at an estimated peak price of Rs {round(expected_price, 2)}/kg."
    }

def analyze_best_buying_window(forecast_df, future_days=30):
    """
    Extracts the best time to buy (lowest price) for traders/exporters 
    within the forecasted window.
    """
    if forecast_df.empty:
        return {"error": "No forecast data generated"}
        
    # Get only the future predictions
    future_forecast = forecast_df.tail(future_days).copy()
    future_forecast['ds'] = pd.to_datetime(future_forecast['ds'])
    
    # Find the day with the minimum forecasted price (yhat)
    min_row = future_forecast.loc[future_forecast['yhat'].idxmin()]
    
    best_date = min_row['ds'].strftime('%Y-%m-%d')
    expected_price = float(min_row['yhat'])
    lower_bound = float(min_row['yhat_lower'])
    upper_bound = float(min_row['yhat_upper'])
    
    return {
        "recommended_buy_date": best_date,
        "expected_price_rs_kg": round(expected_price, 2),
        "confidence_interval": {
            "lower": round(lower_bound, 2),
            "upper": round(upper_bound, 2)
        },
        "message": f"Optimal bulk buying window is around {best_date} at an estimated price of Rs {round(expected_price, 2)}/kg."
    }
