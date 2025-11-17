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

    with httpx.Client(timeout=30.0) as client:
        try:
            resp = client.post(gen_url, json=gen_payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = _extract_text_from_response(data)
            if text:
                return text
            # if no text extracted, return full JSON string
            return str(data)
        except httpx.HTTPStatusError as e:
            # If 404, try chat completions fallback below
            if e.response.status_code != 404:
                _LOGGER.exception("Mistral generate endpoint failed: %s", e)
                raise
        except Exception:
            _LOGGER.exception("Unexpected error calling Mistral generate endpoint")

        # Fallback: try chat/completions endpoint (model + messages)
        chat_url = f"{MISTRAL_BASE_URL.rstrip('/')}/v1/chat/completions"
        chat_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = client.post(chat_url, json=chat_payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = _extract_text_from_response(data)
            if text:
                return text
            return str(data)
        except Exception as e:
            _LOGGER.exception("Mistral chat/completions call failed: %s", e)
            raise
