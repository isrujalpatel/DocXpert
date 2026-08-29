"""
font_normalizer.py — Font detection & normalization service.

Detects every font used in a DOCX document, reports rogue fonts,
and normalizes everything to a single typographic standard.
Also supports applying individual font/margin changes from SuggestedChange items.
"""

from pathlib import Path
from typing import List
from dataclasses import dataclass

from services.document_parser import parse_docx


@dataclass
class FontReport:
    """Report on a single font found in the document."""
    font_name: str
    font_size: float | None
    occurrences: int
    is_target: bool


def detect_fonts(file_path: Path) -> List[FontReport]:
    """
    Detect all fonts used in a DOCX document.

    Args:
        file_path: Path to the .docx file.

    Returns:
        List of FontReport objects, one per unique font+size combination.
    """
    parsed = parse_docx(file_path)
    return [
        FontReport(
            font_name=f["font_name"],
            font_size=f.get("font_size"),
            occurrences=f["occurrences"],
            is_target=False,
        )
        for f in parsed.fonts_used
    ]


def normalize_fonts(
    file_path: Path,
    target_font: str = "Times New Roman",
    target_size: float = 12.0,
) -> dict:
    """
    Normalize all fonts in a DOCX document to a single font and size.

    Args:
        file_path: Path to the .docx file.
        target_font: The font name to normalize to.
        target_size: The font size (in pt) to normalize to.

    Returns:
        dict with keys: output_path, fonts_found, fonts_normalized
    """
    from docx import Document
    from docx.shared import Pt

    from utils.helpers import generate_uuid
    from config.settings import settings

    doc = Document(str(file_path))
    fonts_before = detect_fonts(file_path)
    normalized_count = 0

    for para in doc.paragraphs:
        for run in para.runs:
            changed = False

            if run.font.name != target_font:
                run.font.name = target_font
                changed = True

            if run.font.size is None or run.font.size.pt != target_size:
                run.font.size = Pt(target_size)
                changed = True

            if changed:
                normalized_count += 1

    # Save normalized document
    output_name = f"{generate_uuid()}.docx"
    output_path = settings.UPLOAD_DIR / output_name
    doc.save(str(output_path))

    # Mark the target font in the report
    for report in fonts_before:
        if report.font_name == target_font and report.font_size == target_size:
            report.is_target = True

    return {
        "output_path": output_path,
        "fonts_found": fonts_before,
        "fonts_normalized": normalized_count,
    }
