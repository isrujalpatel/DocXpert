"""
document.py — Data models for documents, suggestions, and API responses.

These models are plain Python dataclasses/dicts used by Flask routes.
The SuggestedChange schema is the shared format used across features 4, 6, 7, and 8.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime
from enum import Enum

from utils.helpers import generate_uuid


# ── Enums ──────────────────────────────────────────────────────

class FileType(str, Enum):
    DOC = "doc"
    DOCX = "docx"
    PDF = "pdf"


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChangeType(str, Enum):
    """Types of suggested changes returned by AI features."""
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    FORMATTING = "formatting"
    FONT = "font"
    MARGIN = "margin"
    LAYOUT = "layout"
    HEADING = "heading"
    SPACING = "spacing"
    LIST_STYLE = "list_style"
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"


class ChangeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ChangeSource(str, Enum):
    LANGUAGETOOL = "languagetool"
    GROQ = "groq"
    DIFFLIB = "difflib"
    SYSTEM = "system"


# ── Location ───────────────────────────────────────────────────

@dataclass
class ChangeLocation:
    """Where in the document a change applies."""
    paragraph_index: int = -1
    run_index: int = -1
    char_offset: int = -1
    char_length: int = 0
    section: str = "body"          # body, header, footer, table
    table_index: int = -1          # if section == "table"
    row_index: int = -1
    cell_index: int = -1
    context: str = ""              # surrounding text snippet

    def to_dict(self) -> dict:
        return asdict(self)


# ── Suggested Change ──────────────────────────────────────────

@dataclass
class SuggestedChange:
    """
    Shared data structure for all AI-generated suggestions.

    Used by: spell check (feature 7), formatting enhancement (feature 4),
    font/margin adjustment (feature 6), document comparison (feature 5),
    and the accept/reject system (feature 8).
    """
    id: str = field(default_factory=lambda: f"chg_{generate_uuid()[:8]}")
    type: str = "spelling"          # ChangeType value
    location: ChangeLocation = field(default_factory=ChangeLocation)
    original: str = ""
    suggested: str = ""
    explanation: str = ""
    confidence: float = 0.0
    status: str = "pending"         # ChangeStatus value
    source: str = "system"          # ChangeSource value

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "SuggestedChange":
        """Create a SuggestedChange from a dictionary."""
        location_data = data.pop("location", {})
        if isinstance(location_data, dict):
            location = ChangeLocation(**{
                k: v for k, v in location_data.items()
                if k in ChangeLocation.__dataclass_fields__
            })
        else:
            location = location_data

        return cls(
            location=location,
            **{k: v for k, v in data.items()
               if k in cls.__dataclass_fields__ and k != "location"}
        )


# ── Response Helpers ──────────────────────────────────────────

def success_response(message: str, data: dict = None) -> dict:
    """Standard success response."""
    resp = {"success": True, "message": message}
    if data:
        resp["data"] = data
    return resp


def error_response(message: str, detail: str = None) -> dict:
    """Standard error response."""
    resp = {"success": False, "error": message}
    if detail:
        resp["detail"] = detail
    return resp
