import spacy
from dotenv import load_dotenv

load_dotenv()

nlp = None

TICKER_MAPPING = {
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "tata consultancy": "TCS.NS",
    "tata consultancy services": "TCS.NS",
    "infosys": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfc": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "wipro": "WIPRO.NS",
    "sbi": "SBIN.NS",
    "state bank": "SBIN.NS",
    "state bank of india": "SBIN.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "hul": "HINDUNILVR.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "indigo": "INDIGO.NS",
    "interglobe": "INDIGO.NS",
    "nifty": "^NSEI",
    "sensex": "^BSESN",
    "nifty 50": "^NSEI",
    "bse": "^BSESN",
    "nse": "^NSEI",
}

def load_nlp():
    global nlp
    if nlp is None:
        print("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        print("spaCy loaded successfully")

def extract_entities(text):
    load_nlp()

    doc = nlp(text)

    entities = {
        "organizations": [],
        "tickers": [],
        "money": [],
        "percentages": [],
    }

    for ent in doc.ents:
        if ent.label_ == "ORG":
            org_name = ent.text.strip()
            if org_name not in entities["organizations"]:
                entities["organizations"].append(org_name)

            ticker = map_to_ticker(org_name)
            if ticker and ticker not in entities["tickers"]:
                entities["tickers"].append(ticker)

        elif ent.label_ == "MONEY":
            entities["money"].append(ent.text.strip())

        elif ent.label_ == "PERCENT":
            entities["percentages"].append(ent.text.strip())

    return entities

def map_to_ticker(entity_name):
    entity_lower = entity_name.lower().strip()

    if entity_lower in TICKER_MAPPING:
        return TICKER_MAPPING[entity_lower]

    for key, ticker in TICKER_MAPPING.items():
        if key in entity_lower or entity_lower in key:
            return ticker

    return None

def extract_tickers_from_articles(articles):
    all_tickers = set()

    for article in articles:
        text = article.get("full_text", "")
        entities = extract_entities(text)
        for ticker in entities["tickers"]:
            all_tickers.add(ticker)

    return list(all_tickers)


if __name__ == "__main__":
    test_texts = [
        "Reliance Industries shares rose 3% after strong quarterly results",
        "RBI policy decision sends Sensex up 400 points, SBI and HDFC Bank lead gains",
        "TCS reports ₹12,000 crore profit, Infosys misses estimates by 5%",
        "Nifty 50 crosses 23,500 as FII buying continues in IT and banking stocks",
    ]

    print("Testing spaCy NER...\n")
    for text in test_texts:
        entities = extract_entities(text)
        print(f"Text: {text}")
        print(f"Organizations: {entities['organizations']}")
        print(f"Tickers: {entities['tickers']}")
        print(f"Money: {entities['money']}")
        print(f"Percentages: {entities['percentages']}")
        print()