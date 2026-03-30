import re
from typing import Optional

# Common words to ignore when extracting keywords
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "shall", "can", "not", "we", "our", "you", "your", "they",
    "their", "it", "its", "this", "that", "as", "by", "from", "into",
    "through", "during", "including", "plus", "also", "both", "between",
    "experience", "looking", "must", "who", "what", "how", "work", "working",
    "able", "good", "strong", "excellent", "understanding", "knowledge",
    "ability", "skills", "skill", "team", "role", "join", "us", "new",
    "within", "across", "up", "out", "about", "more", "other", "such",
}

# Tech and domain keywords to always treat as single tokens even if multi-word
COMPOUND_KEYWORDS = [
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "data science", "software engineering",
    "continuous integration", "continuous deployment", "ci/cd",
    "test driven development", "agile methodology", "rest api", "rest apis",
    "version control", "object oriented", "microservices", "cloud computing",
    "devops", "full stack", "front end", "back end", "api gateway",
]


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text."""
    lower = text.lower()

    # Extract compound keywords first
    found_compounds = []
    for compound in COMPOUND_KEYWORDS:
        if compound in lower:
            found_compounds.append(compound)
            lower = lower.replace(compound, "")

    # Extract single-word tokens
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#._-]{1,}\b", lower)
    single_keywords = [
        t for t in tokens
        if t not in STOPWORDS and len(t) > 2
    ]

    # Deduplicate preserving order
    seen = set()
    result = []
    for kw in found_compounds + single_keywords:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)

    return result


def score_match(cv_parsed: dict, job_description: str) -> dict:
    """
    Compare a parsed CV dict against a job description.
    Returns score (0-100), matched keywords, missing keywords, and extracted job keywords.
    """
    job_keywords = extract_keywords(job_description)

    # Build a searchable text blob from the CV
    cv_text_parts = [
        cv_parsed.get("raw_text", ""),
        cv_parsed.get("summary", "") or "",
        " ".join(cv_parsed.get("skills", [])),
    ]
    for exp in cv_parsed.get("experience", []):
        cv_text_parts.append(exp.get("title", ""))
        cv_text_parts.append(exp.get("company", ""))
        cv_text_parts.extend(exp.get("bullets", []))
    for edu in cv_parsed.get("education", []):
        cv_text_parts.append(edu.get("degree", ""))

    cv_text = " ".join(cv_text_parts).lower()

    matched = []
    missing = []

    for kw in job_keywords:
        if kw in cv_text:
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(job_keywords)
    score = round((len(matched) / total) * 100) if total > 0 else 0

    return {
        "score": score,
        "total_keywords": total,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "job_keywords": job_keywords,
    }
