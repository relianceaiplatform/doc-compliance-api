# app/services/compliance_service.py
import logging
from typing import Any, Dict, List

import language_tool_python

from app.config import MISTRAL_API_KEY, LANGUAGE_TOOL_LANG
from .mistral_client import generate_text


_LOGGER = logging.getLogger(__name__)

# initialize LanguageTool (local by default)
try:
	_tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANG)
except Exception:
	# fallback to public API instance if local initialization fails
	_tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANG)


def analyze_text(text: str, doc_id: str = None) -> Dict[str, Any]:
	if not text or not text.strip():
		return {"doc_id": doc_id, "filename": None, "summary": "No extractable text", "issues": []}

	# LanguageTool matches
	matches = _tool.check(text)
	issues: List[Dict[str, Any]] = []
	for m in matches:
		issues.append({
			"category": "grammar/style",
			"severity": "high" if getattr(m, "ruleIssueType", None) == "grammar" else "medium",
			"sentence": getattr(m, "context", "") or "",
			"message": getattr(m, "message", ""),
			"suggestion": (m.replacements[0] if getattr(m, "replacements", None) else None),
			"offset_start": getattr(m, "offset", None),
			"offset_end": (getattr(m, "offset", None) or 0) + (getattr(m, "errorLength", 0) or 0),
		})

	summary = "LanguageTool analysis completed."

	# optionally ask Mistral to summarize high-level issues & suggestions
	if MISTRAL_API_KEY:
		try:
			prompt = (
				"You are a writing compliance assistant. Provide a short (1-3 sentences) summary of issues and "
				"a bullet list of up to 8 high-level suggestions for improving the document. Return as plain text.\n\n"
				+ text[:15000]
			)
			resp_text = generate_text(prompt, model="mistral-medium", max_tokens=500, temperature=0.0)
			summary = resp_text.strip()
		except Exception as e:
			_LOGGER.exception("Mistral summary failed")
			summary = f"LanguageTool done. Mistral summary failed: {e}"

	return {"doc_id": doc_id, "summary": summary, "issues": issues}
