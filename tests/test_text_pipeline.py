from pathlib import Path

import pytest

from clinical_note_summarization.data.adapters import load_mimic_iv_note, load_public_pilot
from clinical_note_summarization.data.preprocessing import chunk_text, normalize_placeholders, split_sections
from clinical_note_summarization.extraction.baseline import lead_k, textrank


ROOT = Path(__file__).parents[1]


def test_public_pilot_uses_common_schema():
    records = load_public_pilot(ROOT / "data" / "public_pilot" / "notes.csv")
    assert len(records) == 3
    assert records[0].source == "public_pilot"
    assert records[0].reference_summary


def test_mimic_adapter_reads_same_columns():
    records = load_mimic_iv_note(ROOT / "data" / "public_pilot" / "notes.csv")
    assert records[0].source == "mimic_iv_note"


def test_section_splitter_and_placeholder_handling():
    sections = split_sections("HOSPITAL COURSE:\nPain improved with ___.\nDISCHARGE PLAN:\nFollow up.")
    assert [section.title for section in sections] == ["HOSPITAL COURSE", "DISCHARGE PLAN"]
    assert "[REDACTED]" in sections[0].text
    assert "___" not in normalize_placeholders("Dose ___ mg")


def test_chunker_has_overlap_and_validates_window():
    chunks = chunk_text("one two three four five six seven", max_tokens=4, overlap=1)
    assert chunks[0].text == "one two three four"
    assert chunks[1].text.startswith("four")
    with pytest.raises(ValueError):
        chunk_text("text", max_tokens=3, overlap=3)


def test_extractive_baselines_return_source_sentences():
    note = "First sentence. Second sentence has fever. Third sentence has fever."
    assert lead_k(note, 2) == "First sentence. Second sentence has fever."
    assert "fever" in textrank(note, 1)
