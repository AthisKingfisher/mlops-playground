"""A minimal text classifier using Naive Bayes.

Kept intentionally simple: the engineering around it (API, tests,
container, CI) is the point, not the model's sophistication.
Training data is loaded from data/training_data.csv.
"""
import csv
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Resolve the data file relative to THIS file, not the working directory,
# so it works whether run from the project root, in tests, or in a container.
_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "training_data.csv"


def _load_training_data(path: Path = _DATA_PATH) -> tuple[list[str], list[str]]:
    """Load (texts, labels) from a CSV with 'text' and 'label' columns."""
    texts: list[str] = []
    labels: list[str] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


class SentimentClassifier:
    """Wraps a scikit-learn pipeline behind a simple predict() method."""

    def __init__(self) -> None:
        texts, labels = _load_training_data()
        self._pipeline = Pipeline([
            ("vectorizer", CountVectorizer()),
            ("model", MultinomialNB()),
        ])
        self._pipeline.fit(texts, labels)

    def predict(self, text: str) -> dict:
        """Return the predicted label and the model's confidence."""
        label = self._pipeline.predict([text])[0]
        proba = self._pipeline.predict_proba([text]).max()
        return {"label": label, "confidence": round(float(proba), 4)}