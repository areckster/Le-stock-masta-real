"""Sentiment analysis module using a quantized model."""

from typing import List
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)
import torch

_pipeline = None


def _load_pipeline():
    """Load the quantized Mistral 7B INT4 model."""
    global _pipeline
    if _pipeline is None:
        print("Loading sentiment model")
        model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _pipeline


def compute_sentiment(texts: List[str]) -> float:
    """Compute average sentiment score for a list of texts."""
    if not texts:
        return 0.0
    sentiment_pipe = _load_pipeline()
    results = sentiment_pipe(texts)
    scores = []
    for res in results:
        label = res["label"].lower()
        score = res["score"] if label == "positive" else -res["score"]
        scores.append(score)
    avg = float(sum(scores) / len(scores))
    print(f"Computed sentiment: {avg}")
    return avg
