# app/services/rewrite_service.py
from typing import Optional

from .mistral_client import generate_text


def rewrite_text(text: str) -> str:
	"""Rewrite text using Mistral `mistral-medium`.

	Keeps behavior similar to previous OpenAI-driven implementation: short prompt,
	preserve meaning, correct grammar and clarity, and return only corrected text.
	"""
	if not text or not text.strip():
		return ""

	prompt = (
		"You are an expert editor. Rewrite the given text to correct grammar, improve clarity, "
		"and follow standard English writing rules while preserving meaning. Return ONLY the corrected text "
		"(no commentary).\n\n"
		+ text[:15000]
	)

	corrected = generate_text(prompt, model="mistral-medium", max_tokens=2000, temperature=0.0)
	return corrected
