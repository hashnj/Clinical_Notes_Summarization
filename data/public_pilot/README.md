# Synthetic public pilot

`notes.csv` contains three hand-written, non-patient discharge-style examples.
It contains no copied MIMIC/PhysioNet content and has no external clinical
dataset license or provenance claim. The file is committed so the notebook and
unit tests are runnable while access to restricted data is pending.

The schema is:

| Column | Required | Meaning |
| --- | --- | --- |
| `note_id` | yes | Stable local identifier |
| `text` | yes | Discharge-style source note |
| `reference_summary` | no | Pilot-only reference for later comparison |

Replace this file locally, or point the notebook at an authorized export, only
after documenting its source, version, access terms, and split policy.
