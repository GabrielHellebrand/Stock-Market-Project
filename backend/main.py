from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from predictor import (
    train_and_predict_quarterly,
    fetch_stock_data,
    plot_quarterly_prediction_image,
    predict_sp500_quarterly,
    plot_stocks_history
)

app = FastAPI(title="Finance Tracker API")

@app.get("/")
def read_root():
    return {"message": "Finance Tracker API is running!"}

@app.get("/predict/quarterly/{symbol}")
def quarterly_prediction(symbol: str):
    try:
        result = train_and_predict_quarterly(symbol)
        return result
    except Exception as e:
        print(f"Error in /predict/quarterly/{symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/quarterly/{symbol}/chart", response_class=StreamingResponse)
def get_prediction_chart(symbol: str):
    try:
        result = train_and_predict_quarterly(symbol)
        df = fetch_stock_data(symbol)
        image_stream = plot_quarterly_prediction_image(df, result["predicted_close_in_60_days"], symbol)
        return StreamingResponse(image_stream, media_type="image/png")
    except Exception as e:
        print(f"Error in /predict/quarterly/{symbol}/chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/predict/sp500")
def predict_sp500(limit: int = 500):
    """
    Predict quarterly prices for the top N S&P 500 tickers.
    Default limit=20 for performance; adjust as needed.
    """
    try:
        results = predict_sp500_quarterly(limit=limit)
        return {"count": len(results), "predictions": results}
    except Exception as e:
        print(f"Error in /predict/sp500: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/stocks/history/chart")

def stocks_history_chart(tickers: list[str] = Query(default=["AAPL", "MSFT", "TSLA"])):
    """
    Return a PNG chart showing closing price history for given tickers.
    Example: /stocks/history/chart?tickers=AAPL&tickers=MSFT&tickers=TSLA
    """
    try:
        image_stream = plot_stocks_history(tickers)
        return StreamingResponse(image_stream, media_type="image/png")
    except Exception as e:
        print(f"Error in /stocks/history/chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))