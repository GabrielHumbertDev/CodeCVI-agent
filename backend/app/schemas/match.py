from pydantic import BaseModel
import uuid


class MatchRequest(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID


class CategoryScore(BaseModel):
    category: str        # "skills" | "experience" | "education" | "summary"
    matched: list[str]
    missing: list[str]
    score: int           # 0-100


class MatchReport(BaseModel):
    cv_id: uuid.UUID
    job_id: uuid.UUID

    # Overall
    overall_score: int
    grade: str           # "Excellent" | "Good" | "Fair" | "Poor"
    explanation: str     # plain-English summary paragraph

    # Category breakdown
    category_scores: list[CategoryScore]

    # Highlights
    top_strengths: list[str]    # matched keywords worth highlighting (up to 8)
    critical_gaps: list[str]    # most important missing keywords (up to 8)

    # Raw lists (kept for backward compatibility)
    score: int
    total_keywords: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    job_keywords: list[str]
