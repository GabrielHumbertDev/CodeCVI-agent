"""
Coaching service: generate actionable improvement tips from match gaps.
Rule-based (no AI call needed) — fast and always available.
"""
from app.services.match_engine import score_match, _grade

# ---------------------------------------------------------------------------
# Tip library keyed by category
# ---------------------------------------------------------------------------

_SKILL_TIPS = [
    "Add a dedicated Skills section listing {gap} explicitly.",
    "Include {gap} in your technical skills — it appears prominently in this job description.",
    "Consider gaining or demonstrating experience with {gap} through a side project or course.",
]

_EXP_TIPS = [
    "Your experience section does not mention {gap}. Add bullet points that highlight work involving {gap}.",
    "Quantify results related to {gap} (e.g., 'improved {gap} pipeline by 30%').",
    "If you have indirect experience with {gap}, reframe existing bullets to make it explicit.",
]

_EDU_TIPS = [
    "The job values {gap}. If you studied related topics, list relevant coursework or certifications.",
    "A short online certification in {gap} would strengthen your education section for this role.",
]

_SUMMARY_TIPS = [
    "Weave '{gap}' into your professional summary to signal alignment immediately.",
    "Your summary should mention {gap} — hiring managers scan summaries first.",
]

_GENERAL_TIPS = [
    "Tailor this CV specifically for the job by emphasising your {gap} background.",
    "Mirror the job description language: use '{gap}' exactly as it appears.",
]

_CATEGORY_TIPS = {
    "skills": _SKILL_TIPS,
    "experience": _EXP_TIPS,
    "education": _EDU_TIPS,
    "summary": _SUMMARY_TIPS,
}


def _pick_tip(category: str, gap: str, index: int) -> str:
    tips = _CATEGORY_TIPS.get(category, _GENERAL_TIPS)
    tip = tips[index % len(tips)]
    return tip.format(gap=gap)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_coaching_tips(
    cv_parsed: dict,
    job_description: str,
    max_tips: int = 8,
) -> dict:
    """
    Run a match then produce per-gap coaching tips.
    Returns a dict with match_summary and a list of coaching tips.
    """
    report = score_match(cv_parsed, job_description)

    overall_score = report["overall_score"]
    grade = report["grade"]
    category_scores = report["category_scores"]
    critical_gaps = report["critical_gaps"]

    # Build per-category gap tips
    tips = []
    seen_gaps: set[str] = set()

    # Sort categories by score ascending (most in need of improvement first)
    sorted_cats = sorted(category_scores, key=lambda c: c["score"])

    for cat in sorted_cats:
        cat_name = cat["category"]
        missing = cat["missing"]
        for i, gap in enumerate(missing):
            if gap in seen_gaps:
                continue
            if gap not in critical_gaps:
                continue  # only tip on high-priority gaps
            seen_gaps.add(gap)
            tips.append({
                "category": cat_name,
                "gap": gap,
                "tip": _pick_tip(cat_name, gap, i),
                "priority": "high" if i < 3 else "medium",
            })
            if len(tips) >= max_tips:
                break
        if len(tips) >= max_tips:
            break

    # If very few critical tips, add general ones
    if len(tips) < 3:
        for i, gap in enumerate(critical_gaps[:max_tips - len(tips)]):
            if gap not in seen_gaps:
                seen_gaps.add(gap)
                tips.append({
                    "category": "general",
                    "gap": gap,
                    "tip": _GENERAL_TIPS[i % len(_GENERAL_TIPS)].format(gap=gap),
                    "priority": "high",
                })

    # Overall coaching headline
    if overall_score >= 80:
        headline = "Your CV is an excellent match. Minor tweaks to close remaining gaps could push it to near-perfect."
    elif overall_score >= 60:
        headline = "Good match overall. Focus on the high-priority gaps below to significantly strengthen your application."
    elif overall_score >= 40:
        headline = "Fair match. Tailoring your CV around the gaps below will meaningfully improve your chances."
    else:
        headline = "Low match score. Consider carefully reviewing the job requirements and substantially tailoring your CV."

    return {
        "overall_score": overall_score,
        "grade": grade,
        "headline": headline,
        "top_strengths": report["top_strengths"],
        "critical_gaps": critical_gaps,
        "tips": tips,
        "category_scores": [
            {
                "category": c["category"],
                "score": c["score"],
                "matched_count": len(c["matched"]),
                "missing_count": len(c["missing"]),
            }
            for c in category_scores
        ],
    }
