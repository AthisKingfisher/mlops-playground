FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for layer caching (deps change rarely).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code AND the data the extractor loads at startup.
COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]