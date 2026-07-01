"""FastAPI application exposing the sentiment classifier."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.classifier import SentimentClassifier

app = FastAPI(
    title="Sentiment API",
    description="A minimal NLP service: classify text sentiment.",
    version="0.1.0",
)

# Build the classifier once at startup, not per-request.
classifier = SentimentClassifier()


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, examples=["I really enjoyed this"])


class PredictResponse(BaseModel):
    label: str
    confidence: float


@app.get("/health")
def health() -> dict:
    """Liveness check - used later by Docker and Kubernetes."""
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    result = classifier.predict(request.text)
    return PredictResponse(**result)