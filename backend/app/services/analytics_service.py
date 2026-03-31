"""
Analytics service: aggregate stats for the user's dashboard.
"""
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import uuid

from app.models.cv import CV, CVVersion
from app.models.job import Job
from app.models.application import Application
from app.services.match_engine import score_match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_score(cv_parsed: dict | None, job_desc: str | None) -> int | None:
    """Run match engine; return None if data is missing."""
    if not cv_parsed or not job_desc:
        return None
    try:
        return score_match(cv_parsed, job_desc)["overall_score"]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Application funnel
# ---------------------------------------------------------------------------

def application_funnel(db: Session, user_id: uuid.UUID) -> dict:
    """
    Count applications per status bucket.
    Returns funnel dict + conversion rates.
    """
    apps = db.query(Application).filter(Application.user_id == user_id).all()

    STATUS_ORDER = ["draft", "applied", "interview", "offer", "rejected", "withdrawn"]
    counts: Counter = Counter(a.status for a in apps)

    funnel = [
        {"status": s, "count": counts.get(s, 0)}
        for s in STATUS_ORDER
    ]

    total = len(apps)
    applied = counts.get("applied", 0) + counts.get("interview", 0) + counts.get("offer", 0)
    interviews = counts.get("interview", 0) + counts.get("offer", 0)
    offers = counts.get("offer", 0)

    return {
        "total_applications": total,
        "funnel": funnel,
        "conversion_rates": {
            "application_rate": round(applied / total * 100) if total else 0,
            "interview_rate": round(interviews / applied * 100) if applied else 0,
            "offer_rate": round(offers / interviews * 100) if interviews else 0,
        },
    }


# ---------------------------------------------------------------------------
# Score trend
# ---------------------------------------------------------------------------

def score_trend(db: Session, user_id: uuid.UUID, cv_id: uuid.UUID) -> dict:
    """
    For each CVVersion of a given CV, compute match score against its linked job.
    Returns list of {version_number, score, grade, created_at, job_title}.
    """
    from app.services.match_engine import _grade

    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == user_id).first()
    if not cv:
        return {"cv_id": str(cv_id), "trend": []}

    trend = []
    for version in sorted(cv.versions, key=lambda v: v.version_number):
        job = version.job
        score = _safe_score(version.tailored_data, job.description if job else None)
        if score is None:
            continue
        trend.append({
            "version_number": version.version_number,
            "cv_version_id": str(version.id),
            "score": score,
            "grade": _grade(score),
            "job_title": job.title if job else None,
            "job_company": job.company if job else None,
            "created_at": version.created_at.isoformat(),
        })

    # Compute improvement delta
    delta = None
    if len(trend) >= 2:
        delta = trend[-1]["score"] - trend[0]["score"]

    return {
        "cv_id": str(cv_id),
        "cv_filename": cv.filename,
        "version_count": len(trend),
        "score_delta": delta,
        "trend": trend,
    }


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

def dashboard_summary(db: Session, user_id: uuid.UUID) -> dict:
    """
    Aggregate top-level stats for the user's dashboard.
    """
    from app.services.match_engine import _grade

    cvs = db.query(CV).filter(CV.user_id == user_id).all()
    jobs = db.query(Job).filter(Job.user_id == user_id).all()
    apps = db.query(Application).filter(Application.user_id == user_id).all()

    # --- Match scores for all versions that have a linked job ---
    all_scores = []
    for cv in cvs:
        for version in cv.versions:
            if version.job and cv.parsed_data:
                s = _safe_score(version.tailored_data, version.job.description)
                if s is not None:
                    all_scores.append(s)

    avg_score = round(sum(all_scores) / len(all_scores)) if all_scores else None

    # --- Recent applications (last 30 days) ---
    cutoff = datetime.utcnow() - timedelta(days=30)
    recent_apps = [a for a in apps if a.created_at >= cutoff]

    # --- Status breakdown ---
    status_counts = Counter(a.status for a in apps)

    # --- Best performing CV version ---
    best_version = None
    best_score = -1
    for cv in cvs:
        for version in cv.versions:
            if version.job and cv.parsed_data:
                s = _safe_score(version.tailored_data, version.job.description)
                if s is not None and s > best_score:
                    best_score = s
                    best_version = {
                        "cv_version_id": str(version.id),
                        "cv_filename": cv.filename,
                        "job_title": version.job.title,
                        "score": s,
                        "grade": _grade(s),
                    }

    return {
        "totals": {
            "cvs": len(cvs),
            "jobs": len(jobs),
            "applications": len(apps),
            "cv_versions": sum(len(cv.versions) for cv in cvs),
        },
        "applications_last_30_days": len(recent_apps),
        "status_breakdown": dict(status_counts),
        "match_scores": {
            "average": avg_score,
            "count": len(all_scores),
            "grade": _grade(avg_score) if avg_score is not None else None,
        },
        "best_performing_version": best_version,
    }
