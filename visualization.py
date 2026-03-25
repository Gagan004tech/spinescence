import plotly.graph_objs as go
import os

def plot_forecast(commodity, historical_df, forecast_df):
    """
    Plots historical vs forecasted prices using Plotly and saves locally to HTML.
    Returns the URL/path to the saved file.
    """
    if forecast_df.empty or historical_df.empty:
        return None
        
    fig = go.Figure()

    # Historical Prices
    fig.add_trace(go.Scatter(
        x=historical_df['ds'],
        y=historical_df['y'],
        mode='lines',
        name='Historical Data',
        line=dict(color='#00d2ff')
    ))

    # Forecast Prices
    # 'ds', 'yhat', 'yhat_lower', 'yhat_upper'
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'],
        y=forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#ff0055', dash='dash')
    ))
    
    # Confidence Intervals
    fig.add_trace(go.Scatter(
        x=list(forecast_df['ds']) + list(forecast_df['ds'])[::-1],
        y=list(forecast_df['yhat_upper']) + list(forecast_df['yhat_lower'])[::-1],
        fill='toself',
        fillcolor='rgba(0, 210, 255, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='Confidence Interval'
    ))

    fig.update_layout(
        title=f"{commodity} Price Forecast (Next 30 Days)",
        xaxis_title="Date",
        yaxis_title="Price (Rs/kg)",
        template="plotly_dark",
        plot_bgcolor="rgba(17, 24, 39, 1)",
        paper_bgcolor="rgba(17, 24, 39, 1)",
        font=dict(family="Space Grotesk, sans-serif", color="#f8fafc"),
        hovermode="x unified"
    )
    
    filename = f"static/{commodity.lower()}_forecast.html"
    fig.write_html(filename)
    
    return filename
