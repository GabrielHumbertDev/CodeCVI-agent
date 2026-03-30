import httpx
from app.core.config import get_settings

settings = get_settings()

TIMEOUT = 120.0
MAX_RETRIES = 2


async def call_ai(prompt: str, system_prompt: str = "") -> str:
    """
    Call the AI service POST /generate endpoint.
    Returns the generated text string.
    Raises RuntimeError if all retries fail.
    """
    payload = {
        "prompt": prompt,
        "system_prompt": system_prompt,
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    f"{settings.ai_service_url}/generate",
                    json=payload,
                )
                response.raise_for_status()
                return response.json()["text"]
        except httpx.TimeoutException:
            last_error = f"AI service timed out (attempt {attempt})"
        except httpx.ConnectError:
            last_error = "AI service is not reachable. Is it running on port 8001?"
            break  # No point retrying if service is down
        except httpx.HTTPStatusError as e:
            last_error = f"AI service returned error {e.response.status_code}: {e.response.text}"
            break
        except Exception as e:
            last_error = f"Unexpected error calling AI service: {e}"

    raise RuntimeError(last_error)
