# Local Data and Report Images

Keep all source material and generated clinical content local. The following layout is the intended convention; create folders locally as needed:

```text
data/
	raw/
		images/       Authorized report images and PDFs
		text/          Authorized machine-readable notes/transcriptions
	interim/
		ocr/           Unreviewed OCR output and page/region metadata
	processed/
		text/          Reviewed OCR text and prepared text datasets
	external/        Other authorized source datasets
outputs/           Local summaries, evaluation artifacts, and reports
```

These paths are ignored by Git. Do not add real report images or note-level examples to tests, notebooks, screenshots, issue reports, or documentation. Use synthetic fixtures for tests.

Follow the applicable source-specific credentialing, data-use, storage, and sharing requirements. MIMIC-IV-Note is machine-readable text; it does not provide report images for OCR evaluation. Select a separately authorized image source and confirm permission for local processing, OCR, and any derived transcriptions before use.

Treat images, OCR transcripts, corrected text, identifiers, evidence spans, and generated summaries as sensitive. OCR text remains sensitive even when it is derived from an image. Do not commit raw images, note-level data, OCR output, identifiers, local model files, notebook outputs containing clinical content, or generated predictions. Avoid external OCR or model APIs unless the applicable terms and consent explicitly permit sending the source content.

Before processing data, record the source/resource version, image or note types, target pairing, inclusion rules, OCR/model versions, and split strategy in project documentation without including restricted content. Preserve source IDs and page/region references locally so extracted text and summary claims can be audited. Store only aggregate, non-identifying metrics in Git when the applicable rules allow it.
