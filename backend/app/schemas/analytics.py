from pydantic import BaseModel
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Coaching
# ---------------------------------------------------------------------------

class CoachingTip(BaseModel):
    category: str
    gap: str
    tip: str
    priority: str  # "high" | "medium"


class CategorySummary(BaseModel):
    category: str
    score: int
    matched_count: int
    missing_count: int


class CoachingReport(BaseModel):
    overall_score: int
    grade: str
    headline: str
    top_strengths: list[str]
    critical_gaps: list[str]
    tips: list[CoachingTip]
    category_scores: list[CategorySummary]


# ---------------------------------------------------------------------------
# Score trend
# ---------------------------------------------------------------------------

class TrendPoint(BaseModel):
    version_number: int
    cv_version_id: uuid.UUID
    score: int
    grade: str
    job_title: Optional[str]
    job_company: Optional[str]
    created_at: str


class ScoreTrendReport(BaseModel):
    cv_id: uuid.UUID
    cv_filename: str
    version_count: int
    score_delta: Optional[int]  # latest - first (positive = improving)
    trend: list[TrendPoint]


# ---------------------------------------------------------------------------
# Application funnel
# ---------------------------------------------------------------------------

class FunnelBucket(BaseModel):
    status: str
    count: int


class ConversionRates(BaseModel):
    application_rate: int   # % of total that progressed past draft
    interview_rate: int     # % of applied that got interviews
    offer_rate: int         # % of interviews that resulted in offers


class ApplicationFunnel(BaseModel):
    total_applications: int
    funnel: list[FunnelBucket]
    conversion_rates: ConversionRates


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class Totals(BaseModel):
    cvs: int
    jobs: int
    applications: int
    cv_versions: int


class MatchScoreSummary(BaseModel):
    average: Optional[int]
    count: int
    grade: Optional[str]


class BestVersion(BaseModel):
    cv_version_id: uuid.UUID
    cv_filename: str
    job_title: str
    score: int
    grade: str


class DashboardSummary(BaseModel):
    totals: Totals
    applications_last_30_days: int
    status_breakdown: dict[str, int]
    match_scores: MatchScoreSummary
    best_performing_version: Optional[BestVersion]
