# Levl — Text Classifier API

A minimal NLP microservice that classifies text sentiment, built to
demonstrate clean API design, testing, containerization, and CI/CD.

> The model is intentionally simple (Naive Bayes). The focus is the
> engineering around it: a tested, containerized, automatically-built service.

## Tech stack

- **FastAPI** — REST API with automatic OpenAPI docs and request validation
- **scikit-learn** — Naive Bayes sentiment classifier
- **Pydantic** — request/response validation
- **pytest** — automated tests (happy path + input validation)
- **Docker** — containerized for reproducible deployment
- **GitHub Actions** — automated lint/test/build pipeline *(coming)*

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000/docs for the interactive API.


## Running on Docker

Start Docker daemon and confirm it's running
```bash
sudo service docker start
docker ps
```

Build image using Docker
```bash
docker build -t levl:0.1.0 .
```

Run image
```bash
docker run -d -p 8000:8000 --name levl-api levl:0.1.0
```

Then open http://localhost:8000/docs for the interactive API.

Stop and Restart
```bash
docker stop levl-api        # stop it
docker start levl-api       # start it again
docker rm -f levl-api       # stop and remove it
```

## Example

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "this is wonderful"}'
# {"label": "positive", "confidence": 0.87}
```

## Endpoints

| Method | Path       | Description                  |
|--------|------------|------------------------------|
| GET    | `/health`  | Liveness check               |
| POST   | `/predict` | Classify text sentiment      |

## Tests

```bash
pytest -v
```