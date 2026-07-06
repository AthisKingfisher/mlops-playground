# 03 — Skill Extractor

Extracts skills from free text (CVs, job ads) using a curated **gazetteer**
with **fuzzy matching**, served as a FastAPI microservice.

> **Why not a transformer model?** This project began by evaluating several
> pre-trained NER models (`Nucha_ITSkillNER_BERT`, `dslim/bert-base-NER`,
> `yashpwr/resume-ner-bert-v2`). All performed poorly on technical skills —
> e.g. missing Docker, Kubernetes, PostgreSQL, or shattering tool names into
> tokens like `Postg` + `##reSQL`. A curated gazetteer proved far more
> reliable for this task, which is consistent with how many production skill
> extractors are actually built.

## How it works

Two-tier matching against a skills list (`data/skills.csv`), where each skill
has a canonical name, optional aliases, and a hard/soft type:

1. **Exact / alias match** — precise; resolves known names and variants
   (e.g. `postgres`, `psql` → `PostgreSQL`). Uses word boundaries so
   `Java` never matches inside `JavaScript`.
2. **Fuzzy match** — a fallback that catches typos (e.g. `kubernets` →
   `Kubernetes`), with a high threshold (88) and a minimum token length to
   avoid false positives.

## API

| Method | Path       | Description                          |
|--------|------------|--------------------------------------|
| GET    | `/health`  | Liveness check                       |
| POST   | `/extract` | Extract skills from a text payload   |

### Example

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Python engineer with Docker, Kubernetes, and teamwork."}'
```

```json
{
  "skills": [
    {"skill": "Docker", "type": "hard", "match": "exact", "score": null},
    {"skill": "Kubernetes", "type": "hard", "match": "exact", "score": null},
    {"skill": "Python", "type": "hard", "match": "exact", "score": null},
    {"skill": "Teamwork", "type": "soft", "match": "exact", "score": null}
  ],
  "count": 4
}
```

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API.

## Known limitations

These are evaluated trade-offs, not oversights:

- **Short skill names** (R, Go, C) are excluded from fuzzy matching to avoid
  false positives; they rely on exact matching only.
- **Multi-word fuzzy matching** is limited: fuzzy runs word-by-word, so a
  misspelled multi-word skill (e.g. `problm solving`) may be missed. Exact
  multi-word matching works fine.
- **Deduplication**: once a skill is matched by any tier, matching stops, so
  output reflects found skills rather than every attempted match.
- **Skills coverage** is a small curated list for now; the design maps
  directly onto the **ESCO** taxonomy (~13k skills, multilingual) as a
  planned data upgrade.
- **Multi-word spacing variants**: a mistyped multi-word skill written as
  separate words (e.g. `java script`) can match a different single-word skill
  (`Java`) via exact matching, rather than the intended `JavaScript`. Fixable
  by adding spacing-variant aliases, but left as a documented edge case.

## Roadmap

- Swap the curated list for the full **ESCO** skills taxonomy.
- Optional transformer model as a *supplementary* "candidate skills" detector
  for terms outside the gazetteer.
- Containerize and deploy to Kubernetes (with a `startupProbe`).