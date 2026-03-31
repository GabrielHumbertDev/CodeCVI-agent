"""
Playwright-assisted apply service.
Visits a job application URL, detects form fields, maps CV data to fields,
and returns a pre-fill plan + screenshot. Does NOT submit anything.

Uses sync Playwright in a thread pool executor to avoid Windows asyncio
subprocess limitations with uvicorn's event loop.
"""
import asyncio
import base64
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

TIMEOUT = 15_000  # ms
_executor = ThreadPoolExecutor(max_workers=2)


# ---------------------------------------------------------------------------
# Field label → CV data mapping heuristics
# ---------------------------------------------------------------------------

FIELD_MAP = {
    "name":          lambda cv: cv.get("name", ""),
    "full.?name":    lambda cv: cv.get("name", ""),
    "first.?name":   lambda cv: cv.get("name", "").split()[0] if cv.get("name") else "",
    "last.?name":    lambda cv: cv.get("name", "").split()[-1] if cv.get("name") else "",
    "email":         lambda cv: cv.get("email", ""),
    "e.?mail":       lambda cv: cv.get("email", ""),
    "phone":         lambda cv: cv.get("phone", "") or "",
    "mobile":        lambda cv: cv.get("phone", "") or "",
    "telephone":     lambda cv: cv.get("phone", "") or "",
    "summary":       lambda cv: cv.get("summary", "") or "",
    "profile":       lambda cv: cv.get("summary", "") or "",
    "cover":         lambda cv: "",
    "linkedin":      lambda cv: "",
    "website":       lambda cv: "",
    "skills":        lambda cv: ", ".join(cv.get("skills", [])),
    "technologies":  lambda cv: ", ".join(cv.get("skills", [])),
    "expertise":     lambda cv: ", ".join(cv.get("skills", [])),
}


def _suggest_value(field_name: str, field_label: str, cv_data: dict) -> Optional[str]:
    text = f"{field_name} {field_label}".lower().strip()
    for pattern, extractor in FIELD_MAP.items():
        if re.search(pattern, text):
            value = extractor(cv_data)
            return value if value else None
    return None


# ---------------------------------------------------------------------------
# Sync implementation (runs in thread)
# ---------------------------------------------------------------------------

def _run_playwright(url: str, cv_data: dict) -> dict:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            title = page.title()
            fields = _detect_fields_sync(page, cv_data)
            screenshot_bytes = page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            filled_count = sum(1 for f in fields if f["has_suggestion"])

            return {
                "url": url,
                "page_title": title,
                "status": "ok",
                "total_fields": len(fields),
                "suggested_fields": filled_count,
                "fields": fields,
                "screenshot_base64": screenshot_b64,
                "error": None,
            }
        except PlaywrightTimeout:
            return {
                "url": url, "page_title": "", "status": "timeout",
                "total_fields": 0, "suggested_fields": 0, "fields": [],
                "screenshot_base64": None,
                "error": f"Page did not load within {TIMEOUT // 1000}s",
            }
        except Exception as e:
            return {
                "url": url, "page_title": "", "status": "error",
                "total_fields": 0, "suggested_fields": 0, "fields": [],
                "screenshot_base64": None, "error": str(e),
            }
        finally:
            browser.close()


def _detect_fields_sync(page, cv_data: dict) -> list[dict]:
    fields = []
    selector = (
        "input:not([type='hidden']):not([type='submit']):not([type='button'])"
        ":not([type='checkbox']):not([type='radio']):not([type='file']), "
        "textarea, select"
    )
    elements = page.query_selector_all(selector)

    for el in elements:
        try:
            if not el.is_visible():
                continue
            tag = el.evaluate("el => el.tagName").lower()
            field_type = el.get_attribute("type") or tag
            field_id = el.get_attribute("id") or ""
            field_name = el.get_attribute("name") or ""
            placeholder = el.get_attribute("placeholder") or ""
            aria_label = el.get_attribute("aria-label") or ""

            label_text = ""
            if field_id:
                label_el = page.query_selector(f"label[for='{field_id}']")
                if label_el:
                    label_text = label_el.inner_text().strip()

            display_label = label_text or aria_label or placeholder or field_name or field_id
            suggested = _suggest_value(field_name, display_label, cv_data)

            fields.append({
                "field_id": field_id,
                "field_name": field_name,
                "field_type": field_type,
                "label": display_label,
                "suggested_value": suggested,
                "has_suggestion": suggested is not None and suggested != "",
            })
        except Exception:
            continue
    return fields


# ---------------------------------------------------------------------------
# Async wrapper — runs sync code in thread pool
# ---------------------------------------------------------------------------

async def analyse_application_page(url: str, cv_data: dict) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_playwright, url, cv_data)
