import yfinance as yf
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stock-history/{ticker}")
def get_stock_history(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        return [
            {"date": date.strftime('%Y-%m-%d'), "price": round(row['Close'], 2)}
            for date, row in hist.iterrows()
        ]
    except Exception as e:
        return {"error": str(e)}

@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d", interval="1d")

        if hist.shape[0] < 10:
            return {"error": "Not enough data to make a prediction."}

        df = hist[["Close"]].copy()
        df["PrevClose"] = df["Close"].shift(1)
        df["Diff"] = df["Close"] - df["PrevClose"]
        df.dropna(inplace=True)
        df["Target"] = df["Close"].shift(-1)
        df.dropna(inplace=True)

        X_train = df[["Close", "PrevClose", "Diff"]][:-1]
        y_train = df["Target"][:-1]
        X_test = df[["Close", "PrevClose", "Diff"]][-1:]

        model = xgb.XGBRegressor(n_estimators=100, max_depth=3)
        model.fit(X_train, y_train)

        prediction = model.predict(X_test)[0]

        return {
            "ticker": ticker.upper(),
            "last_close": round(df["Close"].iloc[-1], 2),
            "predicted_next_close": round(prediction, 2),
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/predict-batch")
def predict_batch(tickers: List[str] = Query(...)):
    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d", interval="1d")

            if hist.shape[0] < 10:
                results.append({"ticker": ticker.upper(), "error": "Not enough data"})
                continue

            df = hist[["Close"]].copy()
            df["PrevClose"] = df["Close"].shift(1)
            df["Diff"] = df["Close"] - df["PrevClose"]
            df.dropna(inplace=True)
            df["Target"] = df["Close"].shift(-1)
            df.dropna(inplace=True)

            X_train = df[["Close", "PrevClose", "Diff"]][:-1]
            y_train = df["Target"][:-1]
            X_test = df[["Close", "PrevClose", "Diff"]][-1:]

            model = xgb.XGBRegressor(n_estimators=100, max_depth=3, verbosity=0)
            model.fit(X_train, y_train)

            prediction = model.predict(X_test)[0]

            results.append({
                "ticker": ticker.upper(),
                "last_close": round(df["Close"].iloc[-1], 2),
                "predicted_next_close": round(prediction, 2)
            })

        except Exception as e:
            results.append({"ticker": ticker.upper(), "error": str(e)})

    return results

@app.get("/predict-sp500")
def predict_sp500(limit: int = 50):
    tickers = get_sp500_tickers()
    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d", interval="1d")

            if hist.shape[0] < 10:
                continue

            df = hist[["Close"]].copy()
            df["PrevClose"] = df["Close"].shift(1)
            df["Diff"] = df["Close"] - df["PrevClose"]
            df.dropna(inplace=True)
            df["Target"] = df["Close"].shift(-1)
            df.dropna(inplace=True)

            X_train = df[["Close", "PrevClose", "Diff"]][:-1]
            y_train = df["Target"][:-1]
            X_test = df[["Close", "PrevClose", "Diff"]][-1:]

            model = xgb.XGBRegressor(n_estimators=100, max_depth=3, verbosity=0)
            model.fit(X_train, y_train)

            prediction = model.predict(X_test)[0]

            results.append({
                "ticker": ticker.upper(),
                "last_close": round(df["Close"].iloc[-1], 2),
                "predicted_next_close": round(prediction, 2),
                "expected_gain": round(prediction - df["Close"].iloc[-1], 2)
            })
        except Exception:
            continue

    results.sort(key=lambda x: x["expected_gain"], reverse=True)
    return results[:limit]

@app.get("/quarterly-predict/{ticker}")
def quarterly_predict(ticker: str):
    try:
        df = yf.download(ticker, period="2y", interval="1d")
        if df.empty:
            return {"error": "No data found"}

        df["Return"] = df["Close"].pct_change()
        df["Lag1"] = df["Close"].shift(1)
        df["Lag5"] = df["Close"].shift(5)
        df["Lag10"] = df["Close"].shift(10)
        df["Lag20"] = df["Close"].shift(20)
        df["MA10"] = df["Close"].rolling(window=10).mean()
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["Target"] = df["Close"].shift(-60)
        df.dropna(inplace=True)

        X = df[["Lag1", "Lag5", "Lag10", "Lag20", "MA10", "MA20", "Return"]]
        y = df["Target"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

        model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
        model.fit(X_train, y_train)

        future_pred = model.predict(X.tail(1))[0]
        last_close = df['Close'].iloc[-1]
        mse = mean_squared_error(y_test, model.predict(X_test))

        return {
            "ticker": ticker.upper(),
            "last_close": round(last_close, 2),
            "predicted_close_in_60_days": round(future_pred, 2),
            "expected_gain": round(future_pred - last_close, 2),
            "model_mse": round(mse, 4)
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/quarterly-predict-plot/{ticker}")
def quarterly_predict_plot(ticker: str):
    try:
        df = yf.download(ticker, period="2y", interval="1d")
        if df.empty:
            return Response(content="No data", media_type="text/plain", status_code=404)

        df["Return"] = df["Close"].pct_change()
        df["Lag1"] = df["Close"].shift(1)
        df["Lag5"] = df["Close"].shift(5)
        df["Lag10"] = df["Close"].shift(10)
        df["Lag20"] = df["Close"].shift(20)
        df["MA10"] = df["Close"].rolling(window=10).mean()
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["Target"] = df["Close"].shift(-60)
        df.dropna(inplace=True)

        X = df[["Lag1", "Lag5", "Lag10", "Lag20", "MA10", "MA20", "Return"]]
        model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
        model.fit(X, df["Target"])
        future_pred = model.predict(X.tail(1))[0]

        df_recent = df[-90:].copy()
        future_date = df_recent.index[-1] + pd.Timedelta(days=60)

        fig, ax = plt.subplots(figsize=(10, 5))
        df_recent['Close'].plot(ax=ax, label='Actual Close', color='blue')
        ax.scatter(future_date, future_pred, color='red', label='Predicted Close')
        ax.axvline(future_date, color='gray', linestyle='--')
        ax.set_title(f"{ticker.upper()} Quarterly Price Prediction")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.legend()
        ax.grid(True)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")

    except Exception as e:
        return Response(content=str(e), media_type="text/plain", status_code=500)

def get_sp500_tickers():
    try:
        df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = df['Symbol'].tolist()
        return [t.replace('.', '-') for t in tickers]
    except Exception as e:
        return []
