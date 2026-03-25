from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import uvicorn
import os
import uvicorn

from data_collection import scrape_spices_board_cardamom, fetch_agmarknet_data
from preprocessing import preprocess_data
from forecasting import train_and_forecast, analyze_best_buying_window, analyze_best_selling_window
from visualization import plot_forecast

app = FastAPI(title="SpiceSense - AI Spice Price Forecaster")

# Mount static folder for charts and static assets
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/forecast")
def get_forecast(commodity: str = "cardamom", role: str = "trader"):
    commodity = commodity.lower().capitalize()
    
    if commodity not in ["Cardamom", "Pepper"]:
        raise HTTPException(status_code=400, detail="Commodity must be 'cardamom' or 'pepper'")
        
    try:
        # 1. Data Collection
        if commodity == "Cardamom":
            raw_df = scrape_spices_board_cardamom()
        else:
            raw_df = fetch_agmarknet_data()
            
        # 2. Preprocessing
        prophet_df = preprocess_data(raw_df)
        
        # 3. Forecasting
        forecast_df = train_and_forecast(prophet_df, periods=30)
        
        # 4. Role-Based trading strategy
        if role.lower() == "farmer":
            insight = analyze_best_selling_window(forecast_df, future_days=30)
        else:
            insight = analyze_best_buying_window(forecast_df, future_days=30)
        
        # 5. Visualization
        chart_path = plot_forecast(commodity, prophet_df, forecast_df)
        chart_url = f"/static/{commodity.lower()}_forecast.html"
        
        return JSONResponse(content={
            "commodity": commodity,
            "role": role,
            "status": "success",
            "insight": insight,
            "chart_url": chart_url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market_summary")
def get_market_summary():
    """Returns a quick summary for farmers on which crop is performing best right now."""
    try:
        # Get latest data
        cardamom_df = scrape_spices_board_cardamom()
        pepper_df = fetch_agmarknet_data()
        
        cardamom_latest = cardamom_df.dropna().iloc[-1]['Price_Rs_kg']
        pepper_latest = pepper_df.dropna().iloc[-1]['Price_Rs_kg']
        
        winner = "Cardamom" if cardamom_latest > pepper_latest else "Pepper"
        
        return JSONResponse(content={
            "cardamom_current_price": cardamom_latest,
            "pepper_current_price": pepper_latest,
            "highest_value_crop": winner,
            "message": f"{winner} is currently trading at a higher premium (Rs {max(cardamom_latest, pepper_latest)}/kg)."
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
