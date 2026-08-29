"""
spell_checker.py — AI spell check service (feature 7).

Uses LanguageTool API for spelling/grammar checking, with
results mapped to the shared SuggestedChange format.
"""

import time
import requests
from typing import List
from pathlib import Path

from config.settings import settings
from services.document_parser import parse_document
from models.document import SuggestedChange, ChangeLocation


def _check_with_languagetool(text: str, offset: int = 0) -> List[dict]:
    """
    Call the LanguageTool API to check a text chunk.

    Returns raw match objects from the API response.
    """
    try:
        response = requests.post(
            settings.LANGUAGETOOL_URL,
            data={
                "text": text,
                "language": settings.LANGUAGETOOL_LANGUAGE,
                "enabledOnly": "false",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("matches", [])
    except requests.RequestException:
        return []


def _match_to_suggestion(
    match: dict,
    paragraph_index: int,
    text: str,
) -> SuggestedChange:
    """Convert a LanguageTool match to a SuggestedChange."""
    offset = match.get("offset", 0)
    length = match.get("length", 0)
    original = text[offset:offset + length] if offset + length <= len(text) else ""

    # Get the best replacement
    replacements = match.get("replacements", [])
    suggested = replacements[0]["value"] if replacements else original

    # Build context (up to 60 chars around the match)
    ctx_start = max(0, offset - 30)
    ctx_end = min(len(text), offset + length + 30)
    context = text[ctx_start:ctx_end].strip()

    # Determine change type
    rule_category = match.get("rule", {}).get("category", {}).get("id", "").lower()
    if "typo" in rule_category or "spell" in rule_category:
        change_type = "spelling"
    elif "grammar" in rule_category:
        change_type = "grammar"
    else:
        change_type = "grammar"

    return SuggestedChange(
        type=change_type,
        location=ChangeLocation(
            paragraph_index=paragraph_index,
            char_offset=offset,
            char_length=length,
            section="body",
            context=context,
        ),
        original=original,
        suggested=suggested,
        explanation=match.get("message", ""),
        confidence=0.92,
        source="languagetool",
    )


def check_text(text: str, paragraph_index: int = 0) -> List[SuggestedChange]:
    """
    Check a text string for spelling/grammar errors using LanguageTool.

    Args:
        text: The text to check.
        paragraph_index: Index of the paragraph in the document.

    Returns:
        List of SuggestedChange objects.
    """
    if not text or len(text.strip()) < 3:
        return []

    matches = _check_with_languagetool(text)

    suggestions = []
    for match in matches:
        suggestion = _match_to_suggestion(match, paragraph_index, text)
        if suggestion.original:  # Skip empty matches
            suggestions.append(suggestion)

    return suggestions


def check_document(file_path: Path) -> List[SuggestedChange]:
    """
    Check an entire document for spelling/grammar errors.

    Chunks the document text and sends to LanguageTool API.
    Includes rate limiting to stay within API limits.

    Args:
        file_path: Path to the document file.

    Returns:
        List of all SuggestedChange objects found.
    """
    parsed = parse_document(file_path)
    all_suggestions = []

    # Process paragraphs in chunks to respect API limits
    # LanguageTool recommends max 10KB per request
    chunk_text = ""
    chunk_start_para = 0
    para_offsets = []  # (paragraph_index, offset_in_chunk)

    for i, para in enumerate(parsed.paragraphs):
        text = para.text.strip()
        if not text:
            continue

        # Check if adding this paragraph would exceed the chunk limit
        if len(chunk_text) + len(text) + 1 > 8000:
            # Process current chunk
            if chunk_text:
                _process_chunk(chunk_text, para_offsets, all_suggestions)
                time.sleep(0.5)  # Rate limiting

            chunk_text = ""
            para_offsets = []

        # Track offset of this paragraph in the chunk
        para_offsets.append((i, len(chunk_text)))
        chunk_text += text + "\n"

    # Process remaining chunk
    if chunk_text:
        _process_chunk(chunk_text, para_offsets, all_suggestions)

    return all_suggestions


def _process_chunk(
    chunk_text: str,
    para_offsets: list,
    all_suggestions: List[SuggestedChange],
):
    """Process a chunk of text and map matches back to paragraph indices."""
    matches = _check_with_languagetool(chunk_text)

    for match in matches:
        match_offset = match.get("offset", 0)

        # Find which paragraph this match belongs to
        para_index = 0
        offset_in_para = match_offset

        for idx, (p_idx, p_offset) in enumerate(para_offsets):
            if idx + 1 < len(para_offsets):
                next_offset = para_offsets[idx + 1][1]
                if match_offset < next_offset:
                    para_index = p_idx
                    offset_in_para = match_offset - p_offset
                    break
            else:
                para_index = p_idx
                offset_in_para = match_offset - p_offset

        # Update the match offset to be paragraph-relative
        adjusted_match = dict(match)
        adjusted_match["offset"] = offset_in_para

        suggestion = _match_to_suggestion(adjusted_match, para_index, chunk_text)
        if suggestion.original:
            all_suggestions.append(suggestion)
