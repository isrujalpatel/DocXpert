"""
doc_comparator.py — Document diff/comparison engine (feature 5).

Compares two documents and returns differences as SuggestedChange
objects for the shared review UI.
"""

from pathlib import Path
from typing import List
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from services.document_parser import parse_document
from models.document import SuggestedChange, ChangeLocation


@dataclass
class ComparisonResult:
    """Result of comparing two documents."""
    differences: List[SuggestedChange] = field(default_factory=list)
    total_differences: int = 0
    similarity_score: float = 0.0
    paragraphs_a: int = 0
    paragraphs_b: int = 0


def _extract_text_pymupdf(file_path: Path) -> List[str]:
    """Extract text from a PDF using PyMuPDF for better quality."""
    try:
        import fitz
        pdf = fitz.open(str(file_path))
        paragraphs = []
        for page in pdf:
            text = page.get_text("text")
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    if line:
                        paragraphs.append(line)
        pdf.close()
        return paragraphs
    except ImportError:
        pass

    # Fallback to document_parser
    parsed = parse_document(file_path)
    return [p.text for p in parsed.paragraphs]


def compare_documents(file_path_a: Path, file_path_b: Path) -> ComparisonResult:
    """
    Compare two documents and return their differences as SuggestedChange objects.

    Uses PyMuPDF for PDF text extraction (better quality than PyPDF2)
    and SequenceMatcher for paragraph-level diffing.
    """
    ext_a = file_path_a.suffix.lower().lstrip(".")
    ext_b = file_path_b.suffix.lower().lstrip(".")

    # Extract text based on file type
    if ext_a == "pdf":
        texts_a = _extract_text_pymupdf(file_path_a)
    else:
        doc_a = parse_document(file_path_a)
        texts_a = [p.text for p in doc_a.paragraphs]

    if ext_b == "pdf":
        texts_b = _extract_text_pymupdf(file_path_b)
    else:
        doc_b = parse_document(file_path_b)
        texts_b = [p.text for p in doc_b.paragraphs]

    result = ComparisonResult(
        paragraphs_a=len(texts_a),
        paragraphs_b=len(texts_b),
    )

    # Use SequenceMatcher for paragraph-level diffing
    matcher = SequenceMatcher(None, texts_a, texts_b)
    result.similarity_score = round(matcher.ratio(), 4)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        elif tag == "replace":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                para_similarity = SequenceMatcher(None, texts_a[i], texts_b[j]).ratio()

                context_a = (texts_a[i][:80] + "...") if len(texts_a[i]) > 80 else texts_a[i]

                result.differences.append(SuggestedChange(
                    type="modification",
                    location=ChangeLocation(
                        paragraph_index=i,
                        section="body",
                        context=context_a,
                    ),
                    original=texts_a[i],
                    suggested=texts_b[j],
                    explanation=f"Text changed (similarity: {para_similarity:.0%})",
                    confidence=round(1.0 - para_similarity, 2),
                    source="difflib",
                ))

            # Handle unequal lengths in replace blocks
            if i2 - i1 > j2 - j1:
                for i in range(i1 + (j2 - j1), i2):
                    result.differences.append(SuggestedChange(
                        type="deletion",
                        location=ChangeLocation(
                            paragraph_index=i,
                            section="body",
                            context=(texts_a[i][:80] + "...") if len(texts_a[i]) > 80 else texts_a[i],
                        ),
                        original=texts_a[i],
                        suggested="",
                        explanation="Paragraph removed in comparison document",
                        confidence=1.0,
                        source="difflib",
                    ))
            elif j2 - j1 > i2 - i1:
                for j in range(j1 + (i2 - i1), j2):
                    result.differences.append(SuggestedChange(
                        type="addition",
                        location=ChangeLocation(
                            paragraph_index=i2,
                            section="body",
                            context=(texts_b[j][:80] + "...") if len(texts_b[j]) > 80 else texts_b[j],
                        ),
                        original="",
                        suggested=texts_b[j],
                        explanation="Paragraph added in comparison document",
                        confidence=1.0,
                        source="difflib",
                    ))

        elif tag == "delete":
            for i in range(i1, i2):
                result.differences.append(SuggestedChange(
                    type="deletion",
                    location=ChangeLocation(
                        paragraph_index=i,
                        section="body",
                        context=(texts_a[i][:80] + "...") if len(texts_a[i]) > 80 else texts_a[i],
                    ),
                    original=texts_a[i],
                    suggested="",
                    explanation="Paragraph removed in comparison document",
                    confidence=1.0,
                    source="difflib",
                ))

        elif tag == "insert":
            for j in range(j1, j2):
                result.differences.append(SuggestedChange(
                    type="addition",
                    location=ChangeLocation(
                        paragraph_index=i1,
                        section="body",
                        context=(texts_b[j][:80] + "...") if len(texts_b[j]) > 80 else texts_b[j],
                    ),
                    original="",
                    suggested=texts_b[j],
                    explanation="Paragraph added in comparison document",
                    confidence=1.0,
                    source="difflib",
                ))

    result.total_differences = len(result.differences)
    return result
