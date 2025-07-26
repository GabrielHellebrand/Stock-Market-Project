from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import yfinance as yf
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = xgb.XGBRegressor()

@app.get("/stocks")
def get_mock_stocks():
    return [
        {"name": "Apple Inc.", "ticker": "AAPL", "price": 210.12, "pe_ratio": 28.4},
        {"name": "Tesla Inc.", "ticker": "TSLA", "price": 890.34, "pe_ratio": 58.7},
        {"name": "Amazon.com Inc.", "ticker": "AMZN", "price": 132.45, "pe_ratio": 75.9}
    ]

@app.get("/predict/{ticker}")
def predict_stock_price(ticker: str):
    df = yf.download(ticker, period="1y")
    df["Tomorrow"] = df["Close"].shift(-1)
    df.dropna(inplace=True)

    X = df[["Close"]]
    y = df["Tomorrow"]
    model.fit(X, y)

    current_price = df["Close"].iloc[-1]

    def forecast(days):
        price = current_price
        for _ in range(days):
            price = model.predict([[price]])[0]
        return round(price, 2)

    return {
        "today": round(current_price, 2),
        "1_day": forecast(1),
        "1_week": forecast(5),
        "1_month": forecast(21),
        "1_year": forecast(252),
        "5_years": forecast(252*5),
        "all": [
            {"label": "Today", "price": round(current_price, 2)},
            {"label": "1 Day", "price": forecast(1)},
            {"label": "1 Week", "price": forecast(5)},
            {"label": "1 Month", "price": forecast(21)},
            {"label": "1 Year", "price": forecast(252)},
            {"label": "5 Years", "price": forecast(252*5)}
        ]
    }

@app.get("/stock-history/{ticker}")
def get_stock_history(ticker: str):
    df = yf.download(ticker, period="1y")
    df.reset_index(inplace=True)
    return {
        "ticker": ticker,
        "history": [
            {"date": row["Date"].strftime("%Y-%m-%d"), "price": row["Close"]}
            for _, row in df.iterrows()
        ]
    }

@app.get("/quarterly-predict-plot/{ticker}")
def quarterly_predict_plot(ticker: str):
    df = yf.download(ticker, period="2y")
    df["Tomorrow"] = df["Close"].shift(-1)
    df.dropna(inplace=True)

    X = df[["Close"]]
    y = df["Tomorrow"]
    model.fit(X, y)

    current_price = df["Close"].iloc[-1]
    predictions = [current_price]
    for _ in range(60):
        current_price = model.predict([[current_price]])[0]
        predictions.append(current_price)

    dates = pd.date_range(start=datetime.now(), periods=61, freq="B")

    plt.figure(figsize=(10, 5))
    plt.plot(dates, predictions, label="Predicted")
    plt.title(f"{ticker} Quarterly Prediction")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

