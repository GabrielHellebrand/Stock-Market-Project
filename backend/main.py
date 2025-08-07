from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import xgboost as xgb
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache(maxsize=100)
def fetch_stock_data(ticker: str, period: str = "2y"):
    try:
        df = yf.download(ticker, period=period)
        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data for {ticker}: {str(e)}")

def prepare_features(df):
    df = df.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["Volatility"] = df["Close"].rolling(window=20).std()
    df["Volume"] = df["Volume"]
    df["Tomorrow"] = df["Close"].shift(-1)
    df.dropna(inplace=True)
    return df

@app.get("/predict/{ticker}")
async def predict_stock_price(ticker: str):
    try:
        df = fetch_stock_data(ticker)
        df = prepare_features(df)

        features = ["Close", "MA20", "MA50", "Volatility", "Volume"]
        X = df[features]
        y = df["Tomorrow"]

        model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1)
        model.fit(X, y)

        current_data = df[features].iloc[-1:].values
        current_price = df["Close"].iloc[-1]

        def forecast(days):
            price = current_price
            data = current_data.copy()
            for _ in range(days):
                pred = model.predict(data)[0]
                price = pred
                # Update features for next prediction
                data[0, 0] = price  # Update Close
                data[0, 1] = (data[0, 1] * 19 + price) / 20  # Update MA20
                data[0, 2] = (data[0, 2] * 49 + price) / 50  # Update MA50
                data[0, 3] = df["Volatility"].iloc[-20:].mean()  # Approximate volatility
                data[0, 4] = df["Volume"].iloc[-1]  # Keep last volume
            return round(price, 2)

        return {
            "ticker": ticker,
            "today": round(current_price, 2),
            "predictions": [
                {"label": "Today", "price": round(current_price, 2)},
                {"label": "1 Day", "price": forecast(1)},
                {"label": "1 Week", "price": forecast(5)},
                {"label": "1 Month", "price": forecast(21)},
                {"label": "1 Year", "price": forecast(252)},
                {"label": "5 Years", "price": forecast(252 * 5)}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock-history/{ticker}")
async def get_stock_history(ticker: str):
    try:
        df = fetch_stock_data(ticker, period="1y")
        df.reset_index(inplace=True)
        return {
            "ticker": ticker,
            "history": [
                {"date": row["Date"].strftime("%Y-%m-%d"), "price": round(row["Close"], 2)}
                for _, row in df.iterrows()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))