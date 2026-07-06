"""FastAPI application exposing the skill extractor."""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.extractor import SkillExtractor

app = FastAPI(
    title="Skill Extractor API",
    description="Extract skills from text using a curated gazetteer with fuzzy matching.",
    version="0.1.0",
)

# Build the extractor once at startup (loads and indexes the skills list).
extractor = SkillExtractor()


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, examples=["5 years with Python and Docker"])


class Skill(BaseModel):
    skill: str
    type: str
    match: str
    score: float | None = None


class ExtractResponse(BaseModel):
    skills: list[Skill]
    count: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    results = extractor.extract(request.text)
    return ExtractResponse(skills=results, count=len(results))