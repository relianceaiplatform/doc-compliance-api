import os
import httpx
from typing import Optional

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY") or os.environ.get("OPENAI_API_KEY")
MISTRAL_BASE_URL = os.environ.get("MISTRAL_BASE_URL", "https://api.mistral.ai")


def generate_text(
    prompt: str,
    model: str = "mistral-medium",
    max_tokens: int = 1000,
    temperature: float = 0.0,
) -> str:
    """Call Mistral HTTP API to generate text.

    Note: The exact response shape from Mistral can vary. This helper attempts to
    handle common shapes (output/outputs/choices) and returns a sensible string.
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError("Mistral API key not configured")

    url = f"{MISTRAL_BASE_URL.rstrip('/')}/v1/models/{model}/generate"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"input": prompt, "temperature": temperature, "max_new_tokens": max_tokens}

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # Attempt to extract textual content from different possible shapes
    if isinstance(data, dict):
        # Shape: {"output": [...]}
        out = data.get("output") or data.get("outputs")
        if out:
            parts = []
            if isinstance(out, list):
                for item in out:
                    if isinstance(item, dict):
                        # common nested content
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
            # try several common fields
            text = None
            if isinstance(first, dict):
                # messages style
                msg = first.get("message")
                if isinstance(msg, dict):
                    text = msg.get("content")
                text = text or first.get("text") or first.get("message")
            if text:
                return text.strip()

        # fallback: maybe top-level `text`
        if "text" in data and isinstance(data["text"], str):
            return data["text"].strip()

    # Last resort: return stringified JSON
    return str(data)
