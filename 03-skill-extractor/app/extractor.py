"""Skill extractor: gazetteer + fuzzy matching.

Matches text against a curated skills list (canonical names + aliases).
Two tiers:
  1. Exact/alias match  - precise, catches known names and variants.
  2. Fuzzy match         - catches typos/variations, with a high threshold
                           and length guardrails to avoid false matches
                           (e.g. Java != JavaScript).
"""
import csv
import re
from pathlib import Path

from rapidfuzz import fuzz

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.csv"
_FUZZY_THRESHOLD = 88          # 0-100; high = strict. Tune this.
_MIN_LEN_FOR_FUZZY = 4         # don't fuzzy-match very short tokens (R, Go, C)


class SkillExtractor:
    def __init__(self) -> None:
        # Build a lookup: every known surface form -> (canonical, type)
        self._lookup: dict[str, tuple[str, str]] = {}
        self._canonicals: list[tuple[str, str]] = []  # (canonical, type)

        with _DATA_PATH.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                canonical = row["canonical"].strip()
                stype = row["type"].strip()
                self._canonicals.append((canonical, stype))
                # the canonical name itself is a match target
                self._lookup[canonical.lower()] = (canonical, stype)
                # each alias maps to the same canonical
                aliases = row.get("aliases", "") or ""
                for alias in aliases.split("|"):
                    alias = alias.strip().lower()
                    if alias:
                        self._lookup[alias] = (canonical, stype)

    def extract(self, text: str) -> list[dict]:
        text_low = text.lower()
        found: dict[str, dict] = {}   # canonical -> result (dedupes)

        # --- Tier 1: exact / alias substring matching ---
        for surface, (canonical, stype) in self._lookup.items():
            # \b = word boundary, so "java" doesn't match inside "javascript"
            pattern = r"\b" + re.escape(surface) + r"\b"
            if re.search(pattern, text_low):
                found[canonical] = {
                    "skill": canonical, "type": stype, "match": "exact",
                }

        # --- Tier 2: fuzzy matching on individual words (for typos) ---
        words = re.findall(r"\b\w[\w+#.-]*\b", text_low)
        for word in words:
            if len(word) < _MIN_LEN_FOR_FUZZY:
                continue
            for canonical, stype in self._canonicals:
                if canonical in found:
                    continue
                score = fuzz.ratio(word, canonical.lower())
                if score >= _FUZZY_THRESHOLD:
                    found[canonical] = {
                        "skill": canonical, "type": stype,
                        "match": "fuzzy", "score": round(score, 1),
                    }

        return sorted(found.values(), key=lambda x: (x["type"], x["skill"]))