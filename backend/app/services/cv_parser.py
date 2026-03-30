import re
import pdfplumber
from docx import Document as DocxDocument
from typing import Optional


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_cv(file_path: str, file_type: str) -> dict:
    """
    Parse a CV file (pdf or docx) and return a structured dict.
    Raises ValueError if the file cannot be read.
    """
    if file_type == "pdf":
        raw_text = _extract_text_pdf(file_path)
    elif file_type == "docx":
        raw_text = _extract_text_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not raw_text or not raw_text.strip():
        raise ValueError("CV file appears to be empty or unreadable.")

    return _structure(raw_text)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_text_pdf(file_path: str) -> str:
    lines = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.append(text)
    return "\n".join(lines)


def _extract_text_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


# ---------------------------------------------------------------------------
# Structure extraction
# ---------------------------------------------------------------------------

def _structure(raw_text: str) -> dict:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    return {
        "name": _extract_name(lines),
        "email": _extract_email(raw_text),
        "phone": _extract_phone(raw_text),
        "summary": _extract_section(lines, ["summary", "profile", "about", "objective"]),
        "experience": _extract_experience(lines),
        "education": _extract_education(lines),
        "skills": _extract_skills(lines),
        "raw_text": raw_text,
    }


def _extract_name(lines: list[str]) -> Optional[str]:
    # First non-empty line that isn't an email/phone/URL is usually the name
    for line in lines[:5]:
        if not re.search(r"[@:/]|\d{5,}", line) and len(line.split()) <= 6:
            return line
    return None


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(\+?[\d\s\-().]{7,20})", text)
    return match.group(0).strip() if match else None


_SECTION_HEADERS = {
    "experience": ["experience", "work experience", "employment", "career history", "work history"],
    "education": ["education", "qualifications", "academic background", "academic history"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "expertise"],
    "summary": ["summary", "profile", "about", "objective", "personal statement"],
}


def _get_section_lines(lines: list[str], header_variants: list[str]) -> list[str]:
    """Return lines belonging to a section, stopping at the next known section."""
    all_headers = [h for variants in _SECTION_HEADERS.values() for h in variants]
    in_section = False
    section_lines = []

    for line in lines:
        lower = line.lower()
        if any(lower == h or lower.startswith(h) for h in header_variants):
            in_section = True
            continue
        if in_section:
            if any(lower == h or lower.startswith(h) for h in all_headers):
                break
            section_lines.append(line)

    return section_lines


def _extract_section(lines: list[str], header_variants: list[str]) -> Optional[str]:
    section_lines = _get_section_lines(lines, header_variants)
    text = " ".join(section_lines).strip()
    return text if text else None


def _extract_skills(lines: list[str]) -> list[str]:
    section_lines = _get_section_lines(lines, _SECTION_HEADERS["skills"])
    skills = []
    for line in section_lines:
        # Split on common delimiters
        parts = re.split(r"[,|•·\t]+", line)
        for part in parts:
            s = part.strip()
            if s and len(s) < 60:
                skills.append(s)
    return skills


def _extract_experience(lines: list[str]) -> list[dict]:
    section_lines = _get_section_lines(lines, _SECTION_HEADERS["experience"])
    entries = []
    current: Optional[dict] = None

    date_pattern = re.compile(
        r"\b(\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\n]{0,30}"
        r"(\d{4}|present|current|now)\b",
        re.IGNORECASE,
    )

    for line in section_lines:
        if date_pattern.search(line):
            if current:
                entries.append(current)
            current = {"title": "", "company": "", "dates": line, "bullets": []}
        elif current:
            if not current["title"]:
                current["title"] = line
            elif not current["company"]:
                current["company"] = line
            else:
                current["bullets"].append(line)

    if current:
        entries.append(current)

    return entries


def _extract_education(lines: list[str]) -> list[dict]:
    section_lines = _get_section_lines(lines, _SECTION_HEADERS["education"])
    entries = []
    current: Optional[dict] = None

    date_pattern = re.compile(r"\b\d{4}\b")

    for line in section_lines:
        if date_pattern.search(line):
            if current:
                entries.append(current)
            current = {"degree": "", "institution": "", "dates": line}
        elif current:
            if not current["degree"]:
                current["degree"] = line
            elif not current["institution"]:
                current["institution"] = line

    if current:
        entries.append(current)

    return entries
