# === Imports === #
import yfinance as yf
import pandas as pd
import datetime

# === PARAMETERS ===
START_DATE = "2024-07-01"
END_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
INTERVAL = "1d"  # '1d', '1wk', or '1mo'

# === Get S&P 500 companies from Wikipedia, get market data from other sites === 
def get_sp500_companies():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    url = "https://finviz.com/#"
    url = "https://www.marketbeat.com/earnings/transcripts/"
    tables = pd.read_html(url)
    sp500_df = tables[0]
    return sp500_df['Symbol'].tolist()

# === Get NASDAQ-100 companies ===
def get_nasdaq100_companies():
    nasdaq100 = yf.Company("^NDX")  # Nasdaq-100 index ticker
    return nasdaq100.constituents.index.tolist()

# === Download historical stock data ===
def download_stock_data(companies, name):
    all_data = {}
    for company in companies:
        try:
            print(f"Downloading {company}...")
            df = yf.download(company, start=START_DATE, end=END_DATE, interval=INTERVAL, progress=False)
            if not df.empty:
                df['Company'] = company
                all_data[company] = df
        except Exception as e:
            print(f"Failed for {company}: {e}")
    if all_data:
        full_df = pd.concat(all_data.values(), axis=0)
        full_df.to_csv(f"{name}_historical_data.csv")
        print(f"{name} data saved to {name}_historical_data.csv")
    else:
        print(f"No data downloaded for {name}.")

# === Incorporate EMA's === #

# === Main === #
if __name__ == "__main__":
    print("Fetching S&P 500 companies...")
    sp500_companes = get_sp500_companies()
    download_stock_data(get_sp500_companies, "sp500")

    print("Fetching NASDAQ-100 companies...")
    nasdaq_companies = get_nasdaq100_companies()
    download_stock_data(get_nasdaq100_companies, "nasdaq100")
