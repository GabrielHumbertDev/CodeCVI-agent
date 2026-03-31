from sqlalchemy.orm import Session
import uuid

from app.models.application import Application
from app.models.cv import CVVersion
from app.models.cover_letter import CoverLetter
from app.services.cv_service import get_cvs_by_user
from app.services.match_engine import score_match


def _grade(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Poor"


def build_readiness_report(
    db: Session,
    application: Application,
    user_id: uuid.UUID,
) -> dict:
    job = application.job

    # ── Match score ──────────────────────────────────────────────────────────
    # Use the first parsed CV belonging to this user
    user_cvs = get_cvs_by_user(db, user_id)
    parsed_cv = next(
        (cv for cv in user_cvs if cv.parse_status == "done" and cv.parsed_data),
        None,
    )
    match_score = None
    match_grade = None
    if parsed_cv:
        result = score_match(parsed_cv.parsed_data, job.description)
        match_score = result["overall_score"]
        match_grade = _grade(match_score)

    # ── Tailored CV version for this job ────────────────────────────────────
    tailored_version = (
        db.query(CVVersion)
        .filter(CVVersion.job_id == job.id)
        .join(CVVersion.cv)
        .filter_by(user_id=user_id)
        .order_by(CVVersion.version_number.desc())
        .first()
    )
    has_tailored_cv = tailored_version is not None

    # ── Cover letter for this job ────────────────────────────────────────────
    cover_letter = (
        db.query(CoverLetter)
        .filter(CoverLetter.job_id == job.id, CoverLetter.user_id == user_id)
        .order_by(CoverLetter.version_number.desc())
        .first()
    )
    has_cover_letter = cover_letter is not None

    # ── Checklist ────────────────────────────────────────────────────────────
    checklist = []

    # 1. CV uploaded and parsed
    cv_ready = parsed_cv is not None
    checklist.append({
        "item": "CV uploaded and parsed",
        "done": cv_ready,
        "action": None if cv_ready else "Upload a CV via POST /cvs/upload",
    })

    # 2. Match score acceptable
    score_ok = match_score is not None and match_score >= 40
    checklist.append({
        "item": f"Match score ≥ 40% (current: {match_score}%)" if match_score is not None else "Match score",
        "done": score_ok,
        "action": None if score_ok else "Consider tailoring your CV to improve the match score",
    })

    # 3. Tailored CV version exists
    checklist.append({
        "item": "Tailored CV version created for this job",
        "done": has_tailored_cv,
        "action": None if has_tailored_cv else "Tailor your CV via POST /tailor",
    })

    # 4. Cover letter written
    checklist.append({
        "item": "Cover letter written for this job",
        "done": has_cover_letter,
        "action": None if has_cover_letter else "Generate a cover letter via POST /cover-letters",
    })

    # 5. Not already applied
    already_applied = application.status not in ("draft",)
    checklist.append({
        "item": "Application not yet submitted",
        "done": not already_applied,
        "action": None if not already_applied else f"Application is already in '{application.status}' status",
    })

    overall_ready = cv_ready and score_ok and not already_applied

    return {
        "application_id": application.id,
        "job_id": job.id,
        "job_title": job.title,
        "job_company": job.company,
        "current_status": application.status,
        "overall_ready": overall_ready,
        "match_score": match_score,
        "match_grade": match_grade,
        "has_tailored_cv": has_tailored_cv,
        "tailored_cv_version_id": tailored_version.id if tailored_version else None,
        "has_cover_letter": has_cover_letter,
        "cover_letter_id": cover_letter.id if cover_letter else None,
        "checklist": checklist,
    }
