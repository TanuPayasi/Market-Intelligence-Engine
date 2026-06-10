import json
from kafka import KafkaConsumer
from src.signals.fusion import process_articles
from src.database.db import save_signal, init_db

KAFKA_TOPIC = "market-news"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

def run_consumer():
    init_db()
    print(f"Starting Kafka consumer — listening to topic '{KAFKA_TOPIC}'")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="market-intelligence-group",
    )

    for message in consumer:
        article = message.value
        print(f"Received article: {article.get('title', '')[:60]}")

        try:
            signals = process_articles([article])
            for signal in signals:
                signal_id = save_signal(signal)
                if signal_id:
                    print(f"Signal saved: {signal['ticker']} — {signal['action']} ({signal['confidence']})")
        except Exception as e:
            print(f"Error processing article: {e}")

if __name__ == "__main__":
    run_consumer()