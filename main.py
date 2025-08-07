from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import xgboost as xgb
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RASA Stock Prediction API", version="1.0.0")

# Updated CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache(maxsize=100)
def fetch_stock_data(ticker: str, period: str = "2y"):
    """Fetch stock data with better error handling"""
    try:
        logger.info(f"Fetching data for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            logger.error(f"No data found for ticker {ticker}")
            raise ValueError(f"No data found for ticker {ticker}")
        
        logger.info(f"Successfully fetched {len(df)} records for {ticker}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching data for {ticker}: {str(e)}")

def prepare_features(df):
    """Prepare features for machine learning model"""
    df = df.copy()
    
    # Calculate technical indicators
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["Volatility"] = df["Close"].rolling(window=20).std()
    df["Volume"] = df["Volume"]
    df["Tomorrow"] = df["Close"].shift(-1)
    
    # Remove NaN values
    df.dropna(inplace=True)
    
    if len(df) < 50:  # Ensure we have enough data
        raise ValueError("Insufficient data for prediction")
    
    return df

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RASA Stock Prediction API is running"}

@app.get("/predict/{ticker}")
async def predict_stock_price(ticker: str):
    """Predict stock price for given ticker"""
    try:
        logger.info(f"Starting prediction for ticker: {ticker}")
        ticker = ticker.upper().strip()
        
        # Validate ticker format
        if not ticker or not ticker.isalpha() or len(ticker) > 5:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        # Fetch and prepare data
        df = fetch_stock_data(ticker)
        df = prepare_features(df)
        
        # Prepare features for model
        features = ["Close", "MA20", "MA50", "Volatility", "Volume"]
        X = df[features]
        y = df["Tomorrow"]
        
        # Train model
        logger.info("Training XGBoost model...")
        model = xgb.XGBRegressor(
            n_estimators=100, 
            learning_rate=0.1,
            random_state=42,
            verbosity=0  # Suppress XGBoost warnings
        )
        model.fit(X, y)
        
        # Get current data for predictions
        current_data = df[features].iloc[-1:].values
        current_price = float(df["Close"].iloc[-1])
        
        def forecast(days):
            """Forecast price for specified number of days"""
            price = current_price
            data = current_data.copy()
            
            for _ in range(days):
                pred = model.predict(data)[0]
                price = float(pred)
                
                # Update features for next prediction
                data[0, 0] = price  # Update Close
                # Update moving averages (simplified)
                data[0, 1] = (data[0, 1] * 19 + price) / 20  # Update MA20
                data[0, 2] = (data[0, 2] * 49 + price) / 50  # Update MA50
                # Keep volatility and volume relatively stable
                data[0, 3] = df["Volatility"].iloc[-20:].mean()
                data[0, 4] = df["Volume"].iloc[-1]
            
            return round(price, 2)
        
        # Generate predictions
        predictions = [
            {"label": "Current", "price": round(current_price, 2)},
            {"label": "1 Day", "price": forecast(1)},
            {"label": "1 Week", "price": forecast(7)},
            {"label": "1 Month", "price": forecast(30)},
            {"label": "3 Months", "price": forecast(90)},
            {"label": "1 Year", "price": forecast(252)}
        ]
        
        result = {
            "ticker": ticker,
            "today": round(current_price, 2),
            "predictions": predictions
        }
        
        logger.info(f"Successfully generated predictions for {ticker}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error for ticker {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/stock-history/{ticker}")
async def get_stock_history(ticker: str):
    """Get historical stock data"""
    try:
        ticker = ticker.upper().strip()
        df = fetch_stock_data(ticker, period="1y")
        df.reset_index(inplace=True)
        
        history = [
            {"date": row["Date"].strftime("%Y-%m-%d"), "price": round(row["Close"], 2)}
            for _, row in df.iterrows()
        ]
        
        return {
            "ticker": ticker,
            "history": history
        }
    except Exception as e:
        logger.error(f"Error getting history for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)