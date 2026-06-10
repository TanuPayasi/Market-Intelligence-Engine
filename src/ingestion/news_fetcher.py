import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

INDIAN_MARKET_QUERIES = [
    "NSE BSE stock market India",
    "Nifty Sensex trading",
    "RBI monetary policy India",
    "Indian economy GDP inflation",
    "SEBI regulation India stocks",
]

def fetch_market_news(query=None, days_back=1, max_articles=20):
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not found in .env file")

    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    search_query = query if query else " OR ".join(INDIAN_MARKET_QUERIES[:2])

    params = {
        "q": search_query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(NEWS_API_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"NewsAPI error: {response.status_code} - {response.json().get('message')}")

    data = response.json()
    articles = data.get("articles", [])

    cleaned = []
    for article in articles:
        if not article.get("title") or not article.get("description"):
            continue
        cleaned.append({
            "title": article["title"],
            "description": article["description"],
            "content": article.get("content", ""),
            "url": article["url"],
            "source": article["source"]["name"],
            "published_at": article["publishedAt"],
            "full_text": f"{article['title']}. {article['description']}",
        })

    return cleaned


if __name__ == "__main__":
    articles = fetch_market_news()
    print(f"Fetched {len(articles)} articles")
    for a in articles[:3]:
        print(f"\nSource: {a['source']}")
        print(f"Title: {a['title']}")
        print(f"Published: {a['published_at']}")