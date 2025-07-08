import yfinance as yf
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib
matplotlib.use('Agg')  # use non-GUI backend
import matplotlib.pyplot as plt
import io

PREDICT_FORWARD_DAYS = 60  # Approx one financial quarter

def fetch_stock_data(symbol: str, period: str = "2y", interval: str = "1d"):
    return yf.download(symbol, period=period, interval=interval)

def create_features_and_target(df: pd.DataFrame, forward_days: int = PREDICT_FORWARD_DAYS):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df['Lag1'] = df['Close'].shift(1)
    df['Lag5'] = df['Close'].shift(5)
    df['Lag10'] = df['Close'].shift(10)
    df['Lag20'] = df['Close'].shift(20)
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Target'] = df['Close'].shift(-forward_days)  # target is future price
    df.dropna(inplace=True)
    features = df[['Lag1', 'Lag5', 'Lag10', 'Lag20', 'MA10', 'MA20', 'Return']]
    target = df['Target']
    return features, target

def train_and_predict_quarterly(symbol: str):
    df = fetch_stock_data(symbol)
    if df.empty:
        raise ValueError("No stock data found for symbol.")

    X, y = create_features_and_target(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, objective="reg:squarederror")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    future_pred = model.predict(X.tail(1))[0]

    return {
        "symbol": symbol.upper(),
        "last_close": float(df['Close'].iloc[-1]),
        "predicted_close_in_60_days": float(future_pred),
        "model_mse": float(mse)
    }

def plot_quarterly_prediction_image(df, prediction_point, symbol):
    df = df.copy()
    df = df[-90:]  # show recent 90 days

    future_index = df.index[-1] + pd.Timedelta(days=PREDICT_FORWARD_DAYS)

    fig, ax = plt.subplots(figsize=(10, 5))
    df['Close'].plot(ax=ax, label='Actual Close', color='blue')

    ax.scatter(future_index, prediction_point, color='red', label='Predicted Close')
    ax.axvline(x=future_index, color='gray', linestyle='--', alpha=0.6)

    ax.set_title(f"{symbol.upper()} Quarterly Price Prediction")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    tickers = df['Symbol'].tolist()
    # Fix tickers with '.' (e.g. BRK.B → BRK-B for yfinance)
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    return tickers
def predict_sp500_quarterly(limit=500):
    tickers = get_sp500_tickers()
    results = []
    for ticker in tickers[:limit]:  # limit to first 20 for demo; remove limit to do all
        try:
            pred = train_and_predict_quarterly(ticker)
            results.append(pred)
        except Exception as e:
            print(f"Error predicting {ticker}: {e}")
    return results
def plot_stocks_history(tickers, period="1y"):
    plt.figure(figsize=(12, 6))
    for ticker in tickers:
        data = yf.download(ticker, period=period, interval="1d")
        if data.empty:
            continue
        plt.plot(data.index, data['Close'], label=ticker)
    plt.title("Stock Price History")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.legend()
    plt.grid(True)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf