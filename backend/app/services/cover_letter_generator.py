from typing import Optional
from pydantic import ValidationError

from app.services.ai_client import call_ai
from app.schemas.ai_output import CoverLetterOutput

MAX_CL_RETRIES = 2

SYSTEM_PROMPT = """You are a professional cover letter writer.
Write a concise, compelling cover letter tailored to the job description.
Use only information from the CV data provided.
Write in first person. Do not use placeholders like [Your Name].
Return plain text only — no markdown, no headers, no JSON."""


def build_prompt(cv_data: dict, job_description: str, company: str = "", retry_note: str = "") -> str:
    name = cv_data.get("name", "the applicant")
    email = cv_data.get("email", "")
    skills = ", ".join(cv_data.get("skills", []))
    summary = cv_data.get("summary", "")

    experience_lines = []
    for exp in cv_data.get("experience", []):
        title = exp.get("title", "")
        company_name = exp.get("company", "")
        dates = exp.get("dates", "")
        if title or company_name:
            experience_lines.append(f"- {title} at {company_name} ({dates})")

    education_lines = []
    for edu in cv_data.get("education", []):
        degree = edu.get("degree", "")
        institution = edu.get("institution", "")
        if degree or institution:
            education_lines.append(f"- {degree} from {institution}")

    cv_summary = f"""
Applicant: {name}
Email: {email}
Summary: {summary}
Skills: {skills}
Experience:
{chr(10).join(experience_lines) if experience_lines else "Not specified"}
Education:
{chr(10).join(education_lines) if education_lines else "Not specified"}
""".strip()

    company_line = f" at {company}" if company else ""
    note = f"\n\nIMPORTANT: {retry_note}" if retry_note else ""

    return f"""Write a cover letter for the following job application{company_line}.

CV INFORMATION:
{cv_summary}

JOB DESCRIPTION:
{job_description}

Write a 3-4 paragraph cover letter. Be specific and professional.{note}"""


def _validate_cover_letter(text: str) -> str:
    """Validate cover letter output against CoverLetterOutput schema. Returns clean text."""
    try:
        output = CoverLetterOutput(text=text)
        return output.text
    except ValidationError as e:
        errors = "; ".join(err["msg"] for err in e.errors()[:2])
        raise ValueError(f"Cover letter output invalid: {errors}")


async def generate_cover_letter(cv_data: dict, job_description: str, company: str = "") -> str:
    """
    Call AI to generate a cover letter. Validates output and retries on failure.
    Returns validated plain-text cover letter.
    """
    last_error: Optional[str] = None
    retry_note = ""

    for attempt in range(1, MAX_CL_RETRIES + 2):
        prompt = build_prompt(cv_data, job_description, company, retry_note)
        raw = await call_ai(prompt, SYSTEM_PROMPT)

        try:
            return _validate_cover_letter(raw)
        except ValueError as e:
            last_error = str(e)
            retry_note = (
                f"Your previous response failed: {last_error}. "
                "Write a proper 3-4 paragraph cover letter in plain text. No JSON, no markdown."
            )
            if attempt <= MAX_CL_RETRIES:
                continue
            raise ValueError(
                f"Cover letter generation failed after {MAX_CL_RETRIES + 1} attempts: {last_error}"
            )

    raise ValueError(f"Cover letter generation failed: {last_error}")
