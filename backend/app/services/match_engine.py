import re
from collections import Counter

# ---------------------------------------------------------------------------
# Stop words & compound keyword list
# ---------------------------------------------------------------------------

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

COMPOUND_KEYWORDS = [
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "data science", "software engineering",
    "continuous integration", "continuous deployment", "ci/cd",
    "test driven development", "agile methodology", "rest api", "rest apis",
    "version control", "object oriented", "microservices", "cloud computing",
    "devops", "full stack", "front end", "back end", "api gateway",
]


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def extract_keywords(text: str) -> list[str]:
    """Extract meaningful unique keywords from text."""
    lower = text.lower()

    found_compounds = []
    for compound in COMPOUND_KEYWORDS:
        if compound in lower:
            found_compounds.append(compound)
            lower = lower.replace(compound, "")

    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#._-]{1,}\b", lower)
    single_keywords = [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    seen: set[str] = set()
    result = []
    for kw in found_compounds + single_keywords:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
    return result


def keyword_frequency(text: str) -> Counter:
    """Count how many times each keyword appears (used to rank gaps by importance)."""
    lower = text.lower()
    counts: Counter = Counter()

    for compound in COMPOUND_KEYWORDS:
        n = lower.count(compound)
        if n:
            counts[compound] += n
            lower = lower.replace(compound, "")

    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#._-]{1,}\b", lower)
    for t in tokens:
        if t not in STOPWORDS and len(t) > 2:
            counts[t] += 1

    return counts


# ---------------------------------------------------------------------------
# CV section text builders
# ---------------------------------------------------------------------------

def _skills_text(cv: dict) -> str:
    return " ".join(cv.get("skills", []))


def _experience_text(cv: dict) -> str:
    parts = []
    for exp in cv.get("experience", []):
        parts.append(exp.get("title", ""))
        parts.append(exp.get("company", ""))
        parts.append(exp.get("description", ""))
        parts.extend(exp.get("bullets", []))
    return " ".join(parts)


def _education_text(cv: dict) -> str:
    parts = []
    for edu in cv.get("education", []):
        parts.append(edu.get("degree", ""))
        parts.append(edu.get("institution", ""))
    return " ".join(parts)


def _summary_text(cv: dict) -> str:
    return cv.get("summary", "") or ""


# ---------------------------------------------------------------------------
# Category scoring
# ---------------------------------------------------------------------------

def _score_category(job_keywords: list[str], section_text: str) -> dict:
    lower = section_text.lower()
    matched = [kw for kw in job_keywords if kw in lower]
    missing = [kw for kw in job_keywords if kw not in lower]
    total = len(job_keywords)
    score = round(len(matched) / total * 100) if total else 0
    return {"matched": matched, "missing": missing, "score": score}


# ---------------------------------------------------------------------------
# Grade helper
# ---------------------------------------------------------------------------

def _grade(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Poor"


# ---------------------------------------------------------------------------
# Explainability summary
# ---------------------------------------------------------------------------

def _build_explanation(
    overall_score: int,
    grade: str,
    category_scores: list[dict],
    top_strengths: list[str],
    critical_gaps: list[str],
) -> str:
    # Find best and worst categories
    scored = sorted(category_scores, key=lambda c: c["score"], reverse=True)
    best = scored[0] if scored else None
    worst = scored[-1] if scored else None

    strengths_str = ", ".join(top_strengths[:4]) if top_strengths else "none identified"
    gaps_str = ", ".join(critical_gaps[:4]) if critical_gaps else "none identified"

    best_line = f" Your {best['category']} section is the strongest match." if best and best["score"] >= 50 else ""
    worst_line = (
        f" The {worst['category']} section has the most room for improvement."
        if worst and worst["score"] < 50 else ""
    )

    return (
        f"Overall match: {overall_score}% ({grade}).{best_line}{worst_line} "
        f"Key strengths already present: {strengths_str}. "
        f"Critical gaps to address: {gaps_str}."
    )


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def score_match(cv_parsed: dict, job_description: str) -> dict:
    """
    Compare a parsed CV against a job description.
    Returns a full match report dict.
    """
    job_keywords = extract_keywords(job_description)
    jd_freq = keyword_frequency(job_description)

    # Full CV text for overall match
    full_cv_text = " ".join([
        cv_parsed.get("raw_text", ""),
        _summary_text(cv_parsed),
        _skills_text(cv_parsed),
        _experience_text(cv_parsed),
        _education_text(cv_parsed),
    ])

    overall = _score_category(job_keywords, full_cv_text)

    # Category breakdowns
    categories = [
        ("skills", _skills_text(cv_parsed)),
        ("experience", _experience_text(cv_parsed)),
        ("education", _education_text(cv_parsed)),
        ("summary", _summary_text(cv_parsed)),
    ]

    category_scores = []
    for name, text in categories:
        result = _score_category(job_keywords, text)
        category_scores.append({
            "category": name,
            "matched": result["matched"],
            "missing": result["missing"],
            "score": result["score"],
        })

    # Top strengths: matched keywords, sorted by JD frequency (most-mentioned first)
    top_strengths = sorted(
        overall["matched"],
        key=lambda kw: jd_freq.get(kw, 0),
        reverse=True,
    )[:8]

    # Critical gaps: missing keywords, sorted by JD frequency
    critical_gaps = sorted(
        overall["missing"],
        key=lambda kw: jd_freq.get(kw, 0),
        reverse=True,
    )[:8]

    overall_score = overall["score"]
    grade = _grade(overall_score)
    explanation = _build_explanation(
        overall_score, grade, category_scores, top_strengths, critical_gaps
    )

    return {
        # Rich report fields
        "overall_score": overall_score,
        "grade": grade,
        "explanation": explanation,
        "category_scores": category_scores,
        "top_strengths": top_strengths,
        "critical_gaps": critical_gaps,
        # Flat fields (backward compat)
        "score": overall_score,
        "total_keywords": len(job_keywords),
        "matched_keywords": overall["matched"],
        "missing_keywords": overall["missing"],
        "job_keywords": job_keywords,
    }
