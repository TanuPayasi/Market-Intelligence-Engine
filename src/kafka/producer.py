import json
from kafka import KafkaProducer
from src.ingestion.news_fetcher import fetch_market_news
import time

KAFKA_TOPIC = "market-news"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

producer = None

def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
    return producer

def publish_news(articles):
    p = get_producer()
    published = 0
    for article in articles:
        p.send(
            KAFKA_TOPIC,
            key=article.get("source", "unknown"),
            value=article,
        )
        published += 1
    p.flush()
    print(f"Published {published} articles to Kafka topic '{KAFKA_TOPIC}'")
    return published

def run_producer(interval_minutes=15):
    print(f"Starting Kafka producer — publishing every {interval_minutes} minutes")
    while True:
        articles = fetch_market_news(max_articles=20)
        publish_news(articles)
        print(f"Sleeping {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    articles = fetch_market_news(max_articles=5)
    publish_news(articles)
    print("Producer test complete")