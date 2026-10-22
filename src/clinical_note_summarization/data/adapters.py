"""Dataset adapters with one stable schema for pilot and MIMIC-IV-Note data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class NoteRecord:
    """A note in the common schema used by all pipeline stages."""

    note_id: str
    text: str
    reference_summary: str | None = None
    source: str = "unknown"


REQUIRED_COLUMNS = {"note_id", "text"}


def read_notes_csv(path: str | Path, source: str) -> list[NoteRecord]:
    """Read a CSV containing ``note_id`` and ``text`` columns.

    ``reference_summary`` is optional. Real MIMIC-IV-Note exports can be
    mapped to this schema without changing downstream preprocessing.
    """
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset file does not exist: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"{csv_path} is missing required columns: {', '.join(sorted(missing))}"
            )
        records = [
            NoteRecord(
                note_id=(row["note_id"] or "").strip(),
                text=(row["text"] or "").replace("\\n", "\n").strip(),
                reference_summary=(row.get("reference_summary") or "").strip() or None,
                source=source,
            )
            for row in reader
        ]

    if any(not record.note_id or not record.text for record in records):
        raise ValueError(f"{csv_path} contains a blank note_id or text value.")
    return records


def load_public_pilot(path: str | Path) -> list[NoteRecord]:
    """Load the committed synthetic pilot dataset."""
    return read_notes_csv(path, source="public_pilot")


def load_mimic_iv_note(path: str | Path) -> list[NoteRecord]:
    """Load an authorized MIMIC-IV-Note export with the common columns.

    The adapter intentionally does not download data or accept credentials.
    Copy or transform an authorized local export to the documented schema.
    """
    return read_notes_csv(path, source="mimic_iv_note")


def iter_records(records: Iterable[NoteRecord]) -> Iterable[NoteRecord]:
    """Yield records while making the adapter boundary explicit for notebooks."""
    yield from records
