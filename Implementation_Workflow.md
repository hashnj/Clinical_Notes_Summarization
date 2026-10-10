# Implementation Workflow

## Research Goal

Build a research prototype that summarizes de-identified clinical notes and tests whether source-evidence verification reduces unsupported or contradictory claims without losing clinically important information.

The primary comparison is between a fixed summarizer's draft and that same draft after a pre-specified verification policy. The project does not claim to eliminate hallucinations or establish clinical safety. It is not for patient care or clinical decision-making.

## Scope

- Text-only clinical notes. OCR, image processing, prediction, and chatbot features are out of scope.
- MIMIC-IV-derived data is the intended downstream data scope. Do not combine MIMIC-III records into the project dataset.
- ClinicalT5 is a candidate baseline, subject to checkpoint access, license/terms, tokenizer and context compatibility, and a provenance check. If the constraint excludes MIMIC-III pretraining as well as MIMIC-III project data, confirm that before adopting a checkpoint.
- A reference-summary dataset is required for supervised fine-tuning and reference-based metrics. Do not assume MIMIC-IV-Note alone supplies paired targets. Verify the exact candidate resource, task definition, schema, access terms, and available patient/admission identifiers before choosing it.
- Keep restricted notes, derived note-level data, model weights, credentials, and note-level predictions out of Git unless the applicable terms explicitly allow a particular artifact to be shared.

## End-to-End Flow

```mermaid
flowchart TD
    A[Resolve data, model, and access constraints] --> B[Audit a small authorized dataset sample]
    B --> C[Define task, split, and evaluation protocol]
    C --> D[Run a fixed summarization baseline]
    D --> E[Manually assess a preselected sample]
    D --> F[Verify claims in shadow mode]
    E --> F
    F --> G[Compare draft and verification policy on the same test cases]
    G --> H[Error analysis and reproducible report]
    H --> I[Optional demo]
    C -. only if paired data and compute are available .-> J[Optional fine-tuning]
    J --> D
```

## Phase 0: Resolve Feasibility

Make a short decision record before downloading data or building around a particular checkpoint.

1. **Task and target:** Specify the note type, the intended summary type, and whether the goal is inference-only evaluation, supervised fine-tuning, or both.
2. **Dataset:** Identify the exact resource/version and verify that input notes and reference summaries are paired as expected. Confirm that any published train/validation/test split and patient/admission identifiers are available. MIMIC-IV-Note and a hospital-course benchmark are related resources, not interchangeable dataset names.
3. **Data rules:** Confirm credentialing, training, data-use agreements, storage location, and restrictions on derived data and model artifacts.
4. **Model:** Confirm access to the selected ClinicalT5 checkpoint, its associated tokenizer, supported software versions, maximum usable input length, and documented pretraining sources.
5. **Compute:** Record available hardware and decide what can be completed on CPU before planning a training run.

**Deliverable:** A brief `research_decisions.md` (or equivalent) recording choices, unresolved questions, and links to authoritative dataset/model documentation. Do not put credentials or restricted data in this record.

**Gate:** If paired references are unavailable, do not promise supervised fine-tuning or ROUGE/BERTScore against references. Revise the experiment to match the available labels and obtain approval for that change.

## Phase 1: Repository and Data Handling

Set up a small Python package, tests, configuration placeholders, and an explicit local-data policy before handling restricted material.

- Keep raw and processed datasets, model checkpoints, local configuration, and generated note-level artifacts in ignored local paths.
- Use synthetic examples for unit tests. Never paste real notes into committed tests, notebooks, logs, screenshots, or issue reports.
- Keep access tokens out of source control and configuration examples.
- Pin and document runtime dependencies when their versions are selected; avoid installing model/training stacks before the model and hardware decisions are known.

**Deliverable:** The installable package scaffold, ignore rules, data-handling instructions, and a passing smoke test.

## Phase 2: Dataset Audit and Task Definition

Start with the smallest authorized sample that is sufficient to understand the data. Do not begin by downloading or processing the full resource.

Check and record:

- Actual columns, row counts, missing or empty inputs/targets, duplicates, and identifier availability.
- How source notes map to targets; inspect authorized examples locally and confirm that the target section is not accidentally included in the input.
- Note type, section boundaries, date/temporal fields, de-identification markers, and any inclusion/exclusion rules.
- Input and target token-length distributions using the selected checkpoint's tokenizer, once available.
- Whether a provided split exists and whether patients or admissions overlap across partitions.

Do not remove punctuation, negation terms, uncertainty markers, medication details, or section structure as generic “cleaning.” Normalize only formatting that has been shown not to change meaning.

**Deliverable:** A data audit report containing aggregate statistics and documented decisions, but no restricted note text.

## Phase 3: Split and Preprocess

- Prefer an official split when its construction is documented and suitable. Otherwise split by patient, or by admission if that is the best supported grouping, so related examples cannot leak across partitions.
- Create and freeze the split before comparing systems. Record the seed, grouping key, exclusions, and counts. If the necessary grouping identifier is unavailable, document that leakage cannot be ruled out and limit the claims accordingly.
- Check the real tokenizer and model context limit. Compare section-aware selection or chunking with truncation on a small sample; measure what source content is retained. Never assume a 512-token limit or blindly truncate to the beginning of a note.
- Make the transformation reproducible and test it with synthetic fixtures, including empty inputs, repeated rows, long notes, negation, and uncertainty.

**Deliverable:** A repeatable split/preprocessing command and a split manifest that contains no note text or credentials.

## Phase 4: Establish a Baseline

Run the selected pretrained checkpoint on a small, fixed set of held-out examples before fine-tuning.

- Confirm the model and tokenizer load from authorized sources and inference completes.
- Fix and record decoding parameters, model revision, input handling, software versions, and random seeds where applicable.
- Inspect outputs for truncation, repetition, unsupported additions, contradictions, omissions, and changes to negation, certainty, medication, or time.
- Save predictions only in the permitted local output location. Do not commit note-level outputs.

If the checkpoint is unavailable, record the blocker and agree on a replacement model before changing the research question. Do not silently substitute a generic model and report it as ClinicalT5.

**Deliverable:** A reproducible baseline run and an initial error log.

## Phase 5: Define Evaluation Before Comparing Systems

Use the same frozen test cases and generation settings for every compared system. Decide the primary outcome and annotation protocol before inspecting final test results.

Measure complementary properties:

- **Reference similarity:** ROUGE, and optionally BERTScore, only when valid paired references are available. These are not measures of clinical correctness.
- **Claim factuality:** Manually reviewed supported, contradicted, and insufficient-evidence claims; report rates with clear denominators.
- **Coverage and preservation:** Important-fact omissions, negation, uncertainty, medication details, and temporality, using a written rubric.
- **Operational cost:** Generation/verification time, memory where relevant, and the share of claims flagged for review.

Manually review a documented sample. Use a second reviewer and adjudication where feasible; otherwise label the annotations as researcher judgments, not clinical validation. Report uncertainty and failure cases. Avoid treating an automatic factuality score as ground truth.

**Deliverable:** A versioned evaluation protocol and annotation rubric.

## Phase 6: Build a Verifier in Shadow Mode

The first verifier should produce an evidence report without changing the draft summary.

1. Split the draft into atomic clinical claims where possible. Keep compound claims distinguishable so that one supported detail does not mask another unsupported detail.
2. Retrieve multiple relevant source spans, not just one sentence. Preserve source offsets or another stable location reference for auditability.
3. Classify each claim as:
   - **Supported:** retrieved evidence supports the same clinical meaning, including polarity, certainty, and time.
   - **Contradicted:** evidence affirmatively conflicts with the claim.
   - **Insufficient evidence:** the available evidence does not establish support or contradiction. Missing a retrieved match is not proof that a claim is false.
4. Record the claim, evidence locations, label, model/score if used, and reason for review. Evaluate the verifier against manually annotated examples, especially negation, uncertainty, medication details, and temporality.
5. Measure retrieval failures separately from classification failures. Check precision/recall or a confusion matrix on the annotated sample before setting any operating threshold.

Start with a transparent retrieval baseline (for example, BM25) and add an entailment model only if it can be run and evaluated under the access and compute constraints. Generic NLI models may misread clinical language; do not assume their labels are reliable without validation.

**Deliverable:** A verifier report containing evidence and flags, with the original summary preserved unchanged.

## Phase 7: Evaluate a Conservative Intervention

Only after shadow-mode performance is measured, evaluate a policy that acts on verifier results. Keep this separate from claim detection.

- Initially retain supported claims and flag contradicted or insufficient-evidence claims for review. Do not automatically delete every claim without a retrieved match.
- If testing automatic revision or removal, define the policy and stopping condition in advance, re-check every changed claim against the original note, and measure newly introduced errors and lost information.
- Compare the draft and post-policy output for the same examples. Report factuality and coverage together; a lower unsupported-claim rate is not an improvement if important content is simply removed.

**Deliverable:** A paired comparison and error analysis. The primary claim is whether verification reduces unsupported/contradictory claims while preserving important information, not whether it eliminates hallucinations.

## Phase 8: Optional Fine-Tuning, Demo, and Report

**Fine-tuning is conditional.** Proceed only if the selected dataset has valid paired targets, model use is permitted, the split is fixed, and a small reproducible training run fits available compute. Compare the fine-tuned model with the pretrained baseline using the same test set; keep the verification comparison paired with each model's own draft.

Build a small Streamlit demonstration only after the data, generation, and verification interfaces are stable. Use authorized examples locally and show evidence/uncertainty rather than presenting a result as clinically approved.

The final report should document the dataset version and access constraints, selection and split, model/checkpoint provenance, preprocessing, context handling, decoding settings, verifier thresholds, annotation protocol, metrics, compute, and representative successes and failures. State limitations and that the system is a research prototype, not a clinical decision tool.

## First Milestone

1. Confirm the dataset/reference pairing and access terms.
2. Confirm the checkpoint choice and provenance constraint.
3. Install the repository scaffold and run its smoke test.
4. Write the decision record and inspect a small authorized sample.
5. Agree on the evaluation split and protocol before generating comparison results.

These are gates, not calendar estimates. Progress depends on access approval, available paired data, and compute.