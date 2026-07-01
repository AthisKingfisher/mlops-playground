"""A minimal text classifier using Naive Bayes.

Kept intentionally simple: the engineering around it (API, tests,
container, CI) is the point, not the model's sophistication.
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Tiny training set: (text, label). Real projects load this from data;
# inline here to keep the focus on the serving layer.
_TRAINING_DATA = [
    ("I love this, it's wonderful", "positive"),
    ("Absolutely fantastic experience", "positive"),
    ("This is great and very helpful", "positive"),
    ("So happy with the result", "positive"),
    ("Terrible, I hated it", "negative"),
    ("This is awful and useless", "negative"),
    ("Very disappointed and frustrated", "negative"),
    ("The worst experience ever", "negative"),
]


class SentimentClassifier:
    """Wraps a scikit-learn pipeline behind a simple predict() method."""

    def __init__(self) -> None:
        texts, labels = zip(*_TRAINING_DATA)
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