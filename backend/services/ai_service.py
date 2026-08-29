"""
ai_service.py — Central Groq AI client for document analysis.

Provides formatting enhancement (feature 4) and font/margin/layout
suggestion (feature 6) via the Groq chat completions API.
"""

import json
import time
from typing import List

from config.settings import settings
from models.document import SuggestedChange, ChangeLocation


def _get_groq_client():
    """Get an initialised Groq client."""
    from groq import Groq
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Set it in your .env file."
        )
    return Groq(api_key=settings.GROQ_API_KEY)


def _call_groq(system_prompt: str, user_prompt: str, max_retries: int = 2) -> str:
    """
    Call Groq chat completions API with retry logic.

    Returns the assistant's response text.
    """
    client = _get_groq_client()

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries and "rate_limit" in str(e).lower():
                time.sleep(2 ** attempt)
                continue
            raise


def _parse_suggestions_from_json(raw_json: str, source: str = "groq") -> List[SuggestedChange]:
    """Parse the Groq JSON response into SuggestedChange objects."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return []

    suggestions = data.get("suggestions", [])
    changes = []

    for s in suggestions:
        loc_data = s.get("location", {})
        location = ChangeLocation(
            paragraph_index=loc_data.get("paragraph_index", -1),
            run_index=loc_data.get("run_index", -1),
            char_offset=loc_data.get("char_offset", -1),
            char_length=loc_data.get("char_length", 0),
            section=loc_data.get("section", "body"),
            context=loc_data.get("context", ""),
        )

        change = SuggestedChange(
            type=s.get("type", "formatting"),
            location=location,
            original=s.get("original", ""),
            suggested=s.get("suggested", ""),
            explanation=s.get("explanation", ""),
            confidence=float(s.get("confidence", 0.8)),
            source=source,
        )
        changes.append(change)

    return changes


def analyze_formatting(paragraphs: list) -> List[SuggestedChange]:
    """
    Feature 4 — AI formatting enhancement.

    Sends document structure to Groq and receives suggestions for
    heading consistency, spacing, list styles, etc.
    """
    # Build a document summary for the AI
    doc_summary = []
    for i, para in enumerate(paragraphs):
        style = getattr(para, "style_name", None) or "Normal"
        font = getattr(para, "font_name", None) or "unknown"
        size = getattr(para, "font_size", None) or "unknown"
        bold = getattr(para, "is_bold", False)
        text_preview = (para.text[:100] + "...") if len(para.text) > 100 else para.text

        doc_summary.append(
            f"[P{i}] style=\"{style}\" font=\"{font}\" size={size}pt "
            f"bold={bold} text=\"{text_preview}\""
        )

    system_prompt = """You are a document formatting expert. Analyze the document structure below and suggest formatting improvements.

Focus on:
- Heading consistency (e.g., if some headings use Heading 1 style and others use bold Normal)
- Spacing irregularities
- List style consistency
- Font size consistency across similar elements
- Missing heading hierarchy

Return a JSON object with this exact structure:
{
  "suggestions": [
    {
      "type": "heading|spacing|list_style|formatting|font",
      "location": {
        "paragraph_index": 0,
        "section": "body",
        "context": "preview of the text"
      },
      "original": "current state description",
      "suggested": "what it should be changed to",
      "explanation": "why this change is recommended",
      "confidence": 0.85
    }
  ]
}

Only suggest changes that would meaningfully improve the document. Be concise."""

    user_prompt = "Analyze this document structure:\n\n" + "\n".join(doc_summary)

    try:
        raw = _call_groq(system_prompt, user_prompt)
        return _parse_suggestions_from_json(raw, source="groq")
    except Exception as e:
        # Return empty list if AI fails — feature degrades gracefully
        return []


def suggest_settings(paragraphs: list, fonts_used: list, user_intent: str = "") -> List[SuggestedChange]:
    """
    Feature 6 — AI font/margin/settings adjustment.

    Suggests font, margin, and layout changes based on document type
    or user intent (e.g., "academic paper", "business letter").
    """
    # Build document profile
    font_summary = ", ".join(
        f"{f.get('font_name', 'unknown')} ({f.get('font_size', '?')}pt, {f.get('occurrences', 0)}x)"
        for f in fonts_used[:10]
    )

    para_count = len(paragraphs)
    word_count = sum(len(p.text.split()) for p in paragraphs)

    system_prompt = """You are a document design expert. Based on the document profile and user intent, suggest optimal font, margin, and layout settings.

Return a JSON object:
{
  "suggestions": [
    {
      "type": "font|margin|layout|spacing",
      "location": {
        "paragraph_index": -1,
        "section": "body",
        "context": "Document-wide setting"
      },
      "original": "current value or state",
      "suggested": "recommended value",
      "explanation": "why this setting is recommended for this document type",
      "confidence": 0.9
    }
  ]
}

For font changes, specify: font name, size.
For margin changes, specify: top, bottom, left, right in inches.
For layout changes, specify: line spacing, paragraph spacing.
Be specific and actionable."""

    user_prompt = f"""Document profile:
- Paragraphs: {para_count}
- Words: {word_count}
- Fonts used: {font_summary}
- User intent: {user_intent or "general document improvement"}

Suggest optimal settings for this document."""

    try:
        raw = _call_groq(system_prompt, user_prompt)
        return _parse_suggestions_from_json(raw, source="groq")
    except Exception:
        return []
