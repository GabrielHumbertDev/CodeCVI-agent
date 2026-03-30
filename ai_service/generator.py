import httpx
from config import get_settings

settings = get_settings()


async def generate(prompt: str, system_prompt: str = "") -> str:
    """
    Send a prompt to Ollama and return the generated text.
    Raises RuntimeError on failure after retries.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 2048,
        },
    }

    last_error = None
    for attempt in range(1, settings.max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                response = await client.post(
                    f"{settings.ollama_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except httpx.TimeoutException as e:
            last_error = f"Timeout on attempt {attempt}: {e}"
        except httpx.HTTPStatusError as e:
            last_error = f"HTTP error on attempt {attempt}: {e.response.status_code}"
            break  # Don't retry on HTTP errors
        except Exception as e:
            last_error = f"Unexpected error on attempt {attempt}: {e}"

    raise RuntimeError(f"AI generation failed after {settings.max_retries} attempts. Last error: {last_error}")
