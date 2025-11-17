import os
import logging
import httpx
from typing import Optional

_LOGGER = logging.getLogger(__name__)

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY") or os.environ.get("OPENAI_API_KEY")
MISTRAL_BASE_URL = os.environ.get("MISTRAL_BASE_URL", "https://api.mistral.ai")


def _extract_text_from_response(data: dict) -> Optional[str]:
    """Try to extract a text string from common response shapes."""
    # Shape: {"output": [...]} or {"outputs": [...]} or simple string
    out = data.get("output") or data.get("outputs")
    if out:
        parts = []
        if isinstance(out, list):
            for item in out:
                if isinstance(item, dict):
                    content = item.get("content")
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and "text" in c:
                                parts.append(c["text"])
                            elif isinstance(c, str):
                                parts.append(c)
                    elif isinstance(content, str):
                        parts.append(content)
                    elif "text" in item:
                        parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
        elif isinstance(out, str):
            parts.append(out)
        if parts:
            return "\n".join(parts).strip()

    # openai-like `choices`
    choices = data.get("choices")
    if choices and isinstance(choices, list):
        first = choices[0]
        if isinstance(first, dict):
            msg = first.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    return content.strip()
            # fallback fields
            text = first.get("text") or first.get("message")
            if isinstance(text, str):
                return text.strip()

    # top-level `text`
    if isinstance(data.get("text"), str):
        return data.get("text").strip()

    return None


def generate_text(
    prompt: str,
    model: str = "mistral-medium",
    max_tokens: int = 1000,
    temperature: float = 0.0,
) -> str:
    """Call Mistral API. Try model generate endpoint first, fall back to chat/completions.

    Some Mistral models expect `/v1/models/{model}/generate` while others (chat-style)
    use `/v1/chat/completions`. This function attempts both and returns extracted text.
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError("Mistral API key not configured")

    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}

    # First try model generate endpoint
    gen_url = f"{MISTRAL_BASE_URL.rstrip('/')}/v1/models/{model}/generate"
    gen_payload = {"input": prompt, "temperature": temperature, "max_new_tokens": max_tokens}

    import time
    import random

    # Simple retry logic with exponential backoff for transient errors (429, 5xx)
    max_attempts = 5
    backoff_base = 1.0

    with httpx.Client(timeout=30.0) as client:
        # Try model generate endpoint first
        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.post(gen_url, json=gen_payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                text = _extract_text_from_response(data)
                return text if text is not None else str(data)
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                # If endpoint not found, break and try fallback
                if status == 404:
                    _LOGGER.debug("Generate endpoint not found for model %s, trying chat fallback", model)
                    break
                # Retry on rate limit or server errors
                if status == 429 or 500 <= status < 600:
                    if attempt == max_attempts:
                        _LOGGER.exception("Mistral generate endpoint failed after %d attempts: %s", attempt, e)
                        raise
                    sleep = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    _LOGGER.warning("Mistral generate rate-limited/server error (status=%s). Retrying in %.1fs (attempt %d/%d)", status, sleep, attempt, max_attempts)
                    time.sleep(sleep)
                    continue
                # Other client errors - do not retry
                _LOGGER.exception("Mistral generate endpoint returned client error: %s", e)
                raise
            except Exception:
                if attempt == max_attempts:
                    _LOGGER.exception("Unexpected error calling Mistral generate endpoint (final attempt)")
                    raise
                sleep = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                _LOGGER.warning("Unexpected error calling Mistral generate endpoint. Retrying in %.1fs (attempt %d/%d)", sleep, attempt, max_attempts)
                time.sleep(sleep)

        # Fallback: try chat/completions endpoint
        chat_url = f"{MISTRAL_BASE_URL.rstrip('/')}/v1/chat/completions"
        chat_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(1, max_attempts + 1):
            try:
                resp = client.post(chat_url, json=chat_payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                text = _extract_text_from_response(data)
                return text if text is not None else str(data)
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429 or 500 <= status < 600:
                    if attempt == max_attempts:
                        _LOGGER.exception("Mistral chat/completions failed after %d attempts: %s", attempt, e)
                        raise
                    sleep = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    _LOGGER.warning("Mistral chat/completions rate-limited/server error (status=%s). Retrying in %.1fs (attempt %d/%d)", status, sleep, attempt, max_attempts)
                    time.sleep(sleep)
                    continue
                _LOGGER.exception("Mistral chat/completions returned client error: %s", e)
                raise
            except Exception as e:
                if attempt == max_attempts:
                    _LOGGER.exception("Unexpected error calling Mistral chat/completions (final attempt): %s", e)
                    raise
                sleep = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                _LOGGER.warning("Unexpected error calling Mistral chat/completions. Retrying in %.1fs (attempt %d/%d)", sleep, attempt, max_attempts)
                time.sleep(sleep)
