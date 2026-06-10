from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "ProsusAI/finbert"

tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading FinBERT model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model.eval()
        print("FinBERT loaded successfully")

def analyze_sentiment(text):
    load_model()

    if not text or len(text.strip()) == 0:
        return {"label": "neutral", "confidence": 0.0, "scores": {}}

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = F.softmax(logits, dim=-1)
    scores = probabilities[0].tolist()

    labels = ["positive", "negative", "neutral"]
    label_scores = {labels[i]: round(scores[i], 4) for i in range(3)}

    predicted_idx = torch.argmax(probabilities, dim=-1).item()
    predicted_label = labels[predicted_idx]
    confidence = scores[predicted_idx]

    return {
        "label": predicted_label,
        "confidence": round(confidence, 4),
        "scores": label_scores,
    }

def analyze_batch(texts, batch_size=8):
    load_model()
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            result = analyze_sentiment(text)
            results.append(result)

    return results

if __name__ == "__main__":
    test_texts = [
        "Reliance Industries reports 40% jump in quarterly profits, beats analyst estimates",
        "RBI raises interest rates unexpectedly, markets fall sharply on inflation fears",
        "Infosys announces new office in Pune, hiring 500 employees",
        "Sensex gains 395 points as banking stocks rally on strong earnings",
        "TCS misses revenue targets for third consecutive quarter amid global slowdown",
    ]

    print("Testing FinBERT sentiment analysis...\n")
    for text in test_texts:
        result = analyze_sentiment(text)
        print(f"Text: {text[:60]}...")
        print(f"Sentiment: {result['label']} (confidence: {result['confidence']})")
        print(f"Scores: {result['scores']}\n")