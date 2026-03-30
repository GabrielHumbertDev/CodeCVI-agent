import json
import re
from typing import Optional
from app.services.ai_client import call_ai


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a professional CV writer. Your job is to tailor a CV to a specific job description.

STRICT RULES:
1. You may ONLY use information present in the original CV data provided.
2. You must NOT invent new skills, qualifications, companies, dates, or achievements.
3. You may rephrase, reorder, and emphasise existing content to better match the job.
4. Return ONLY valid JSON. No explanation, no markdown, no code blocks.
5. Keep the same JSON structure as the input CV data.
"""


def build_prompt(cv_data: dict, job_description: str) -> str:
    cv_json = json.dumps(cv_data, indent=2)
    return f"""Below is the original CV data and a job description.
Tailor the CV to better match the job description.
Only rephrase existing content - do not add anything new.

ORIGINAL CV DATA:
{cv_json}

JOB DESCRIPTION:
{job_description}

Return the tailored CV as valid JSON with the same structure as the original CV data.
Do not wrap in markdown. Return raw JSON only."""


# ---------------------------------------------------------------------------
# Truth validator
# ---------------------------------------------------------------------------

def validate_tailored_cv(original: dict, tailored: dict) -> tuple[bool, list[str]]:
    """
    Check that the tailored CV does not contain fabricated content.
    Returns (is_valid, list_of_violations).
    """
    violations = []
    original_text = _flatten_text(original).lower()

    # Check name hasn't changed
    if tailored.get("name") and original.get("name"):
        if tailored["name"].lower() != original["name"].lower():
            violations.append(f"Name changed from '{original['name']}' to '{tailored['name']}'")

    # Check email hasn't changed
    if tailored.get("email") and original.get("email"):
        if tailored["email"].lower() != original["email"].lower():
            violations.append(f"Email changed from '{original['email']}' to '{tailored['email']}'")

    # Check no new skills were added
    original_skills = {s.lower() for s in original.get("skills", [])}
    for skill in tailored.get("skills", []):
        if skill.lower() not in original_text and skill.lower() not in original_skills:
            violations.append(f"Fabricated skill: '{skill}'")

    # Check experience companies haven't been fabricated
    original_companies = {
        exp.get("company", "").lower()
        for exp in original.get("experience", [])
        if exp.get("company")
    }
    for exp in tailored.get("experience", []):
        company = exp.get("company", "").lower()
        if company and company not in original_text and company not in original_companies:
            violations.append(f"Fabricated company: '{exp.get('company')}'")

    is_valid = len(violations) == 0
    return is_valid, violations


def _flatten_text(data: dict) -> str:
    """Flatten all string values in a dict to a single text blob."""
    parts = []
    for v in data.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(_flatten_text(item))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Main tailor function
# ---------------------------------------------------------------------------

async def tailor_cv(cv_data: dict, job_description: str) -> tuple[dict, bool, list[str]]:
    """
    Call AI to tailor the CV, then validate the output.
    Returns (tailored_data, validation_passed, violations).
    """
    prompt = build_prompt(cv_data, job_description)
    raw_response = await call_ai(prompt, SYSTEM_PROMPT)

    # Extract JSON from response (strip markdown if present)
    json_text = _extract_json(raw_response)

    try:
        tailored = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw response: {raw_response[:500]}")

    is_valid, violations = validate_tailored_cv(cv_data, tailored)

    return tailored, is_valid, violations


def _extract_json(text: str) -> str:
    """Strip markdown code fences if the AI wrapped the JSON."""
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()
