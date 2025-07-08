import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.marketbeat.com"
TRANSCRIPTS_URL = f"{BASE_URL}/earnings/transcripts/"

def fetch_transcript_links(pages=1):
    transcripts = []
    for page in range(1, pages + 1):
        print(f"Fetching page {page}...")
        url = f"{TRANSCRIPTS_URL}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.select("div.earnings-article"):
            title = item.select_one("h3 a")
            date = item.select_one("div.article-date").text.strip()
            if title:
                link = BASE_URL + title['href']
                transcripts.append({
                    "Company": title.text.strip(),
                    "Date": date,
                    "Link": link
                })
        time.sleep(1)  # be nice to the server
    return transcripts

def scrape_transcript_text(link):
    print(f"Scraping transcript: {link}")
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.select_one("div.pb-4.article-body")
    if article:
        return article.get_text(separator="\n").strip()
    return "Transcript not found."

def main(pages_to_scrape=2):
    print("Starting transcript scraper...")
    transcripts = fetch_transcript_links(pages=pages_to_scrape)
    
    # Optional: Add full transcript text to each entry
    for t in transcripts:
        t["Transcript"] = scrape_transcript_text(t["Link"])
        time.sleep(1)

    df = pd.DataFrame(transcripts)
    df.to_csv("earnings_transcripts.csv", index=False)
    print("Done! Saved to 'earnings_transcripts.csv'.")

if __name__ == "__main__":
    main(pages_to_scrape=2)  # Adjust pages as needed