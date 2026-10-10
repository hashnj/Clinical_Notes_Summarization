# Clinical Note Summarization

Research prototype for generating concise summaries from de-identified clinical notes and evaluating whether source-evidence checks reduce unsupported claims without losing important information.

**Status:** Repository setup and research decisions are in progress. This is not a clinical tool.

## Start Here

- [Implementation workflow](Implementation_Workflow.md)
- [Revised proposal slides](Clinical_Note_Summarization_Revised.pptx)
- [Original proposal PDF](Clinical%20Note%20Summarization.pdf)
- [Consolidated proposal notes](#project-background)

## Current Scope and Open Decisions

- The intended task is text-only summarization of de-identified MIMIC-IV clinical notes. OCR, computer vision, and MIMIC-III data are outside the current data scope.
- The exact dataset and note-summary pairing are not yet selected. MIMIC-IV-Note provides notes; do not assume it alone provides the reference summaries needed for supervised training or reference-based evaluation. Verify the candidate benchmark's schema, pairing, access terms, and split identifiers first.
- ClinicalT5 is a candidate baseline, not yet a dependency. Confirm checkpoint access, tokenizer compatibility, context limits, and pretraining provenance. In particular, distinguish excluding MIMIC-III from the project's downstream data from requiring a model that was never pretrained on MIMIC-III.
- The research question is whether evidence-based verification reduces unsupported or contradictory claims while preserving clinically important content.

## Repository Layout

```text
configs/                          Experiment configuration (no credentials)
data/                             Local-only data; see data/README.md
notebooks/                        Exploratory analysis, without committed notes
scripts/                          Reproducible command-line entry points
src/clinical_note_summarization/
   data/                           Dataset validation and preprocessing
   generation/                     Model loading and summary generation
   verification/                   Claim/evidence checks and policy
   evaluation/                     Metrics and review exports
tests/                            Unit tests using synthetic examples
```

## Local Setup

The repository starts with no model or dataset dependencies. In PowerShell, from the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

To inspect authorized CSV data and use notebooks, install the data-analysis tools. Add `pyarrow` only if the selected files are Parquet:

```powershell
.\.venv\Scripts\python.exe -m pip install pandas jupyterlab
# Optional for Parquet files:
.\.venv\Scripts\python.exe -m pip install pyarrow
```

### Optional Model Dependencies

Install these only after confirming dataset access, the model checkpoint, and available hardware. Install PyTorch using the command for your platform and CPU/CUDA configuration from the [official PyTorch selector](https://pytorch.org/get-started/locally/), then install the model libraries:

```powershell
.\.venv\Scripts\python.exe -m pip install transformers sentencepiece accelerate
```

For an initial TF-IDF evidence retriever and ROUGE evaluation:

```powershell
.\.venv\Scripts\python.exe -m pip install scikit-learn rouge-score
```

`bert-score` and `streamlit` are optional follow-on dependencies, not required for the initial repository setup. These commands install packages into the local environment; once the chosen pipeline is settled, record its dependency groups and version constraints in `pyproject.toml`.

### Restricted Data Access

MIMIC-IV access is restricted to credentialed users who have completed the required training and signed the data-use agreement. See the [PhysioNet MIMIC-IV access page](https://physionet.org/content/mimiciv/3.1/) and its [required training](https://physionet.org/content/mimiciv/view-required-training/3.1/).

A Kaggle upload is not, by itself, permission to use restricted MIMIC-IV data. Do not use or redistribute a third-party mirror unless its provenance and authorization explicitly permit that use. PhysioNet also treats MIMIC-derived datasets and models as sensitive; follow its [sharing guidance](https://physionet.org/content/mimiciv/3.1/) and applicable agreements. If access is unavailable, use a dataset that is explicitly authorized for your use and update the project scope accordingly.

Do not put MIMIC data, model weights, credentials, or note-level outputs in Git. Read [data handling notes](data/README.md) before placing any authorized files locally. MIMIC-IV-Note provides clinical notes; verify that the selected task dataset also provides the paired reference summaries needed for supervised training or reference-based evaluation.

## Project Background

### Consolidated project notes from the revised PPT and original PDF

> **Purpose:** A GitHub-ready text record of the two presentations, preserving the project motivation, scope, dataset details, research papers, methodology, and especially the logic represented in the flowcharts.
>
> **Source files:** `Clinical_Note_Summarization_Revised.pptx` (revised proposal) and `Clinical Note Summarization.pdf` (original presentation).
>
> **Important interpretation:** Where the two files differ, this document records the difference explicitly. The revised PPT defines the tighter project scope: **text-only MIMIC-IV-Note + ClinicalT5 + evidence-based factuality verification**. The original PDF contains an earlier, broader workflow with OCR/computer-vision processing and mentions both MIMIC-III and MIMIC-IV.

---

## 1. Project overview

**Title:** Clinical Note Summarization Without Hallucination  
**Programme:** M.Tech, Information Technology, NITK  
**Submitted to:** Dr. Dinesh Naik  
**Team:** Amit Nishad (262IT002), Nikhilesh Joshi (262IT029)

### Core idea

Clinical notes are long, semi-structured narratives that may contain patient history, symptoms, diagnoses, medications, procedures, laboratory findings, and treatment plans. Summarization can reduce the burden of reviewing these notes, but a fluent summary is not necessarily a factually faithful one.

The project aims to generate concise summaries from clinical text and then verify that each generated clinical claim is supported by the original note. Particular attention is given to **negation, uncertainty, contradictions, missing important facts, medication details, diagnoses, and temporality**.

### Main principle

> Every generated clinical claim should be traceable to evidence in the source note.

### Why it matters

- Clinical narratives can be lengthy, repetitive, and difficult to scan quickly.
- A model may invent a diagnosis or medication, change an existing fact, omit an important medicine, or mishandle a negation.
- Lexical overlap with a reference summary does not establish clinical correctness.
- The desired balance is between **compression, coverage, and evidence support**.

### Hallucination terminology from the original presentation

- **Intrinsic hallucination:** Changes or contradicts information already present in the source (the slide's example: changing age 30 to age 45).
- **Extrinsic hallucination:** Adds a new, unverified fact not present in the source (the slide's example: adding a heart surgery).

### Illustrative negation failure

Source note: “Patient denies chest pain. No history of diabetes documented.”  
Unsafe summary: “Patient has chest pain and diabetes.”

The failure is not just poor wording: it reverses the clinical meaning by losing negation.

---

## 2. Research problem, objectives, and scope

### Problem statement

Clinical summarization models can produce concise, readable output, yet generated statements may be unsupported, contradictory, or incomplete relative to the source note. Existing clinical summarization models do not guarantee factual faithfulness, making hallucination a major challenge for healthcare AI.

### Objectives

1. **Build a summarization pipeline:** Generate concise summaries from de-identified MIMIC-IV clinical notes using ClinicalT5.
2. **Improve evidence-grounded factuality:** Check generated claims against source evidence, with attention to negation and uncertainty.
3. **Evaluate quality and clinical reliability:** Measure relevance, coverage, and factual consistency using complementary automatic metrics and targeted human review.
4. **Analyse trade-offs and failure modes:** Compare baseline generation with the verification approach and identify remaining error patterns.

### Revised scope (the current project definition)

**In scope**
- MIMIC-IV clinical text accessed through the companion MIMIC-IV-Note resource.
- ClinicalT5-based summary generation.
- Claim-level evidence support checks.
- Negation and uncertainty preservation.
- Automatic evaluation plus targeted manual review.

**Out of scope**
- OCR and scanned-document processing.
- Computer vision or image understanding.
- Mixing MIMIC-III with MIMIC-IV in the same project.

The revised proposal explicitly frames this as a **text-to-text NLP task**, not an OCR/CV project. The OCR and CV steps in the original PDF are part of the earlier proposed workflow and should not be treated as part of the revised scope unless the project scope is deliberately changed.

---

## 3. Dataset: MIMIC-IV clinical notes

### Dataset choice

- **Source:** De-identified electronic health records from Beth Israel Deaconess Medical Center.
- **Text resource:** MIMIC-IV-Note, the companion resource providing free-text clinical notes.
- **Likely note focus:** Discharge summaries and their associated admission context.
- **Why it fits:** Clinical language includes diagnoses, treatment details, temporal information, and negation.

### Access and handling requirements stated in the revised PPT

- Complete the applicable PhysioNet credentialing and data-use training.
- Use de-identified text and do not attempt re-identification.
- Document note selection, exclusions, train/validation/test split, and preprocessing.
- Do not claim OCR is required for the selected note text: it is already machine-readable.
- Verify access conditions and the exact schema for the selected MIMIC-IV-Note version before data preparation.

### Illustrative schema from the revised PPT

The values below are examples from the slide, **not real patient records**. Exact fields depend on the selected table and version.

| Field | Example shown | Purpose |
|---|---|---|
| `subject_id` | `10001234` | De-identified patient key |
| `hadm_id` | `20004567` | Hospital admission key |
| `note_id` | `NOTE-0001` | Unique note identifier |
| `note_type` | Discharge summary | Select relevant note type |
| `charttime` | `2150-04-12 10:30` | Note timestamp |
| `text` | “Patient admitted with…” | Source clinical narrative |

### Training example

- **Input:** Selected clinical note text.
- **Target:** Reference brief hospital-course summary, where paired labels are available.

### Data-splitting warning

Keep patient/admission-level splits grouped to reduce leakage. Notes from the same patient or admission should not inadvertently leak across training and evaluation splits.

### Dataset discrepancy between the files

- **Original PDF:** Lists “MIMIC-III / MIMIC-IV” and describes ICU records, patient history, diagnoses, and medication.
- **Revised PPT:** Narrows the project to **MIMIC-IV only**, with note text supplied through **MIMIC-IV-Note**. It explicitly says not to mix MIMIC-III and MIMIC-IV.

For the current proposal, follow the revised PPT.

---

## 4. End-to-end workflow: the revised methodology

The revised flowchart shows a text-only pipeline with five main stages, followed by a support decision and correction loop.

```mermaid
flowchart TD
    A["1. Select notes<br/>MIMIC-IV-Note<br/>Discharge summaries"]
    B["2. Prepare data<br/>Clean text and select sections<br/>Tokenize and split"]
    C["3. Generate summary<br/>ClinicalT5 baseline<br/>Note → draft summary"]
    D["4. Extract claims<br/>Split draft into claims<br/>Identify key clinical facts"]
    E["5. Verify evidence<br/>Match claims to source spans<br/>Check support / contradiction"]
    F{"Is the claim supported?"}
    G["Supported: keep claim"]
    H["Unsupported: revise or remove"]
    I["Re-verify revised claims<br/>against the original note"]
    J["Final summary<br/>Concise • evidence-linked<br/>Negation-aware • uncertainty-preserving"]

    A --> B --> C --> D --> E --> F
    F -- Yes --> G --> J
    F -- No --> H --> I --> E
```

### Stage-by-stage meaning

1. **Select notes**
   - Retrieve relevant clinical notes from MIMIC-IV-Note.
   - Focus on discharge summaries for the proposed task.

2. **Prepare data**
   - Clean the text and select relevant sections.
   - Tokenize the text and create train/validation/test splits.
   - Record selection and preprocessing decisions.

3. **Generate a draft**
   - Use ClinicalT5 as the baseline summarization model.
   - Map the source note to a draft summary.

4. **Extract claims**
   - Divide the draft summary into individual clinical statements or claims.
   - Identify the key clinical facts asserted by each statement.

5. **Verify against source evidence**
   - Match each claim to one or more supporting source spans.
   - Check whether the source supports or contradicts the claim.

6. **Branch on support**
   - **Supported:** retain the claim.
   - **Unsupported:** revise or remove the claim.

7. **Correction loop**
   - Find supporting evidence in the original note.
   - Correct or regenerate the statement using that evidence.
   - Re-verify the revised statement before accepting it.

8. **Produce the final summary**
   - Concise.
   - Evidence-linked.
   - Negation-aware.
   - Uncertainty-preserving.

**Important:** The flowchart describes a proposed workflow, not a completed implementation. The slides do not specify the exact claim extractor, evidence-matching algorithm, correction model, thresholds, or stopping condition for the loop. These remain implementation decisions.

---

## 5. Expanded verification logic from the original PDF

The original PDF makes the verification stage more explicit by naming four checks. These checks can be incorporated into the revised claim-verification stage without reintroducing the excluded OCR/CV pipeline.

### Statement-level verification checks

| Check | Question to ask | Example of a failure to detect |
|---|---|---|
| Evidence check | Is the statement supported by the source? | Adding a diagnosis not mentioned in the note |
| Negation check | Are “no,” “not,” and “denies” handled correctly? | Turning “no diabetes” into “diabetes” |
| Uncertainty check | Are “may,” “possible,” and “likely” preserved? | Turning a possible condition into a confirmed diagnosis |
| Omission check | Are important clinical facts missing? | Leaving out a clinically important medication |

### Verification and correction loop

```mermaid
flowchart TD
    A["Draft summary"] --> B["Split into clinical statements"]
    B --> C["Retrieve or match source evidence"]
    C --> D["Evidence check"]
    D --> E["Negation check"]
    E --> F["Uncertainty check"]
    F --> G["Omission / coverage check"]
    G --> H{"All statements adequately supported<br/>and key facts covered?"}
    H -- Yes --> I["Keep verified statements"]
    H -- No --> J["Find supporting evidence"]
    J --> K["Correct, remove, or regenerate statement"]
    K --> C
    I --> L["Final verified clinical summary"]
```

### How to interpret the loop

- The unit of checking is an individual **clinical statement**, not only the summary as a whole.
- A statement should be retained only when the evidence supports it and its clinical meaning is preserved.
- Unsupported claims should be corrected or removed; the corrected version must be checked again.
- The omission check is complementary to hallucination detection: a summary may contain no invented facts and still be incomplete.
- “All statements supported” is not alone enough if clinically important facts have been omitted. The coverage check therefore matters separately.

The original PDF's novelty slide also proposes a table-like representation of extracted facts:

| Clinical fact | Source sentence | Location |
|---|---|---|
| Diabetes | “Patient has a history of diabetes.” | Page 2, Line 5 (illustrative slide example) |

This illustrates the intended evidence trace: a fact should be linked to the sentence and location from which it was extracted. For machine-readable MIMIC-IV-Note text, the exact location representation will depend on how note offsets or section boundaries are stored.

---

## 6. Earlier pipeline in the original PDF — and what changed

The original PDF shows this broad pipeline:

```mermaid
flowchart LR
    A["Dataset<br/>MIMIC-III / MIMIC-IV"] --> B["Preprocessing<br/>Remove symbols, normalize,<br/>tokenize, segment sentences"]
    B --> C["CV + NLP feature extraction<br/>OCR, layout detection,<br/>text-region extraction;<br/>clinical entity extraction"]
    C --> D["Summarization model"]
    D --> E["Faithfulness verification"]
    E --> F["Evaluation metrics"]
```

### Original pipeline components

- **Dataset:** MIMIC-III / MIMIC-IV; patient history, diagnosis, medication, ICU records.
- **Preprocessing:** Remove symbols, normalize text, tokenize, segment sentences; OCR for scanned documents.
- **CV tasks:** OCR, layout detection, image enhancement, and text-region extraction.
- **NLP tasks:** Clinical entity extraction and context understanding.
- **Summarization model:** Generate a summary from extracted/preprocessed content.
- **Faithfulness verification:** Check generated content against the source.
- **Evaluation metrics:** Assess the output.

### Scope decision

The revised PPT removes the CV/OCR stage and selects MIMIC-IV-Note text only. Therefore, the current project pipeline should start with machine-readable notes, not scanned documents or images. Keeping the original pipeline in these notes is useful for understanding the project's evolution, but it should not be confused with the final proposed scope.

---

## 7. Literature review: papers listed in the revised PPT

The revised presentation identifies ten relevant papers/resources. The descriptions below preserve the roles assigned to them in the slides. Some entries are not fully bibliographic; verify exact author lists, titles, venues, and links before using them in a formal report.

### Model and dataset foundations

#### 1. ClinicalT5: A Generative Language Model for Clinical Text
- **Authors/year/venue shown:** Lu, Q., Dou, D., and Nguyen, T. (2022), Findings of EMNLP.
- **Role in the project:** Introduces a T5 model pretrained on clinical text.
- **Relevance:** Foundation for the proposed ClinicalT5 generation baseline.
- **How it informs the design:** Use a clinical-domain-adapted model rather than assuming a generic summarizer will behave adequately on clinical language.

#### 2. MIMIC-IV, a Freely Accessible Electronic Health Record Dataset
- **Authors/year/venue shown:** Johnson, A. E. W., et al. (2023), *Scientific Data*.
- **Role in the project:** Primary dataset description; documents EHR data, clinical measurements, and de-identified records.
- **Relevance:** Dataset provenance and understanding the broader MIMIC-IV resource.
- **Note:** The revised PPT states that free-text notes are accessed through the companion MIMIC-IV-Note resource.

#### 3. A Dataset and Benchmark for Hospital Course Summarization with Adapted Large Language Models
- **Year shown:** 2025; the slide does not provide a full author/venue citation.
- **Role in the project:** Introduces MIMIC-IV-BHC and evaluates hospital-course summaries from clinical notes.
- **Relevance:** A task-specific benchmark/resource for clinical hospital-course summarization.
- **Citation status:** Complete the bibliographic details before formal citation.

#### 4. Clinical-T5: Large Language Models Built Using MIMIC Clinical Text
- **Year/resource shown:** 2023, PhysioNet resource.
- **Role in the project:** Documents Clinical-T5 variants trained using MIMIC clinical notes.
- **Relevance:** Related model/resource information for clinical-text generation.
- **Citation status:** The slide gives a resource title but not a complete author/identifier citation; verify the exact resource record.

### Hallucination detection and factual consistency

#### 5. Better Late Than Never: Model-Agnostic Hallucination Post-Processing Framework Towards Clinical Text Summarization (MEDAL)
- **Authors/year/venue shown:** Li, S., et al. (2024), Findings of ACL.
- **Role in the project:** Model-agnostic post-processing intended to detect and correct hallucinations in medical summaries.
- **Relevance:** Closest conceptual precedent in the slides for a post-generation verification/correction stage.

#### 6. Evaluating the Factual Consistency of Abstractive Text Summarization
- **Authors/year/venue shown:** Kryscinski, W., et al. (2020), EMNLP.
- **Method/resource named in the slide:** FactCC.
- **Role in the project:** Predicts support or contradiction and identifies evidence spans.
- **Relevance:** Motivates claim-level support checks and evidence-span linking.

#### 7. Improving Factual Consistency of Abstractive Text Summarization via Question Answering
- **Authors/year/venue shown:** Nan, F., et al. (2021), ACL-IJCNLP.
- **Role in the project:** Uses question-answering signals to measure and optimize factual consistency.
- **Relevance:** An alternative approach to checking factual agreement between a source and its summary.

#### 8. Enhancing Factual Consistency of Abstractive Summarization
- **Authors/year/venue shown:** Zhu, C., et al. (2021), NAACL-HLT.
- **Role in the project:** Combines fact-aware generation with a factual correction stage.
- **Relevance:** Supports considering correction as well as detection.

#### 9. AlignScore: Evaluating Factual Consistency with a Unified Alignment Function
- **Authors/year/venue shown:** Zha, Y., et al. (2023), ACL.
- **Role in the project:** General-purpose alignment metric for assessing whether generated text is supported by its source.
- **Relevance:** Candidate factual-consistency evaluation metric.
- **Caution from the revised PPT:** It motivates verification but does not guarantee clinical safety; suitability for this task must be validated.

#### 10. Factual Consistency Evaluation of Summarization in the Era of Large Language Models
- **Authors/year/venue shown:** Luo, Z., Xie, Q., and Ananiadou, S. (2024), *Expert Systems with Applications*.
- **Role in the project:** Studies factual-consistency evaluation in the LLM era, including clinical summaries.
- **Relevance:** Motivates careful metric selection rather than relying on a single automatic score.

### Literature synthesis from the revised PPT

- ClinicalT5 is a defensible domain-adapted generation baseline, but it still needs task-specific evaluation.
- MIMIC-IV provides the EHR foundation; note text is accessed through MIMIC-IV-Note.
- MEDAL, FactCC, and AlignScore motivate verification and factuality evaluation, but none should be presented as a guarantee of clinical safety.
- High lexical overlap or fluent output does not prove factual correctness.
- Targeted human review remains important.

### Literature entries in the original PDF that were replaced or flagged

The original PDF listed three less-specific entries:

1. **“Clinical Safety Framework (2025)”** — described as checking hallucinations and missing information. The revised PPT says this is too vague to verify without authors, title, and venue.
2. **“MEDAL (ACL 2024)”** — retained in the revised PPT with a fuller title and description.
3. **“LLM Clinical Note Summarization System (2025)”** — described in the original as using NER + an LLM to identify important clinical information and create summaries. The revised PPT calls this generic and replaces it with the MIMIC-IV-BHC benchmark paper.

Do not cite the vague entries as established papers without locating their exact bibliographic records.

---

## 8. Evaluation plan

The revised PPT explicitly argues that evaluation must measure more than word overlap.

| Evaluation dimension | Metric/check listed | What it tells us | Limitation to keep in mind |
|---|---|---|---|
| Content overlap | ROUGE-1, ROUGE-2, ROUGE-L | Lexical overlap with reference summaries | Does not guarantee factuality |
| Semantic alignment | BERTScore (optional) | Semantic similarity between generated and reference text | Can miss clinically important contradictions |
| Factual consistency | AlignScore or FactCC-style checks | Whether generated content is supported by the source | Must be validated for clinical use |
| Clinical error analysis | Manual review of negation, medications, diagnoses, temporality | Finds clinically meaningful errors and omissions | Review sample and protocol must be documented |

### Recommended reporting details from the revised PPT

Report:
- Model version.
- Decoding settings.
- Data split and note-selection procedure.
- Confidence intervals where feasible.
- Examples of failure cases.
- A stratified manual-review sample.
- Unsupported claims and critical omissions.

### What success means

Reduce unsupported or contradictory claims **while preserving clinically important content**. The aim is not factuality at the expense of coverage, nor a concise summary that loses critical information.

---

## 9. Expected contributions and limitations

### Expected contributions

- ClinicalT5-based summarization baseline.
- Evidence-checking and correction workflow.
- Evaluation of factuality/omission trade-offs.
- Error taxonomy for clinically important failures.

### Limitations stated in the revised PPT

- MIMIC notes reflect one institution and population.
- Reference summaries may not cover every useful fact.
- Automatic factuality metrics can miss clinical nuance.
- Human evaluation is limited and is not a safety certification.

### Safety boundary

This is a **research prototype**, not a clinical decision-making system. Generated summaries must not be presented as a substitute for clinician review.

---

## 10. Practical implementation checklist

The presentations propose the overall workflow but do not specify all implementation choices. This checklist translates the stated plan into decisions that need to be made; it is not a claim that the work has already been completed.

- [ ] Complete the applicable MIMIC-IV / MIMIC-IV-Note access and data-use requirements.
- [ ] Select the exact note table, note type, and inclusion/exclusion rules.
- [ ] Confirm whether usable input/reference-summary pairs are available for the selected task.
- [ ] Define patient/admission-grouped train, validation, and test splits.
- [ ] Document preprocessing and truncation/length handling.
- [ ] Establish the ClinicalT5 baseline and record model/version/decoding settings.
- [ ] Define how summaries will be split into clinical claims.
- [ ] Define how source evidence spans will be retrieved or matched to each claim.
- [ ] Choose and validate the support/contradiction method (for example, a FactCC-style method or AlignScore, as discussed in the slides).
- [ ] Specify checks for negation, uncertainty, temporality, diagnoses, and medication details.
- [ ] Define what happens to unsupported claims: revise, regenerate, or remove.
- [ ] Define a stopping condition for repeated correction and re-verification.
- [ ] Evaluate ROUGE and optionally BERTScore alongside factuality checks.
- [ ] Conduct targeted manual review for unsupported claims, contradictions, and critical omissions.
- [ ] Compare baseline generation with the verification workflow.
- [ ] Record residual failure cases and limitations.

---

## 11. Key terminology

- **Clinical note:** A clinical narrative documenting information such as history, symptoms, diagnosis, medications, procedures, and plans.
- **Abstractive summarization:** Producing a concise summary that may paraphrase source content rather than copying it verbatim.
- **Hallucination:** Generated content that is unsupported by, or inconsistent with, the source.
- **Intrinsic hallucination:** Alteration/contradiction of a source fact.
- **Extrinsic hallucination:** Addition of a fact not established by the source.
- **Evidence span:** A specific part of the source note used to justify a generated claim.
- **Claim-level verification:** Checking individual clinical statements against source evidence.
- **Negation preservation:** Maintaining distinctions such as “has” versus “does not have” or “denies.”
- **Uncertainty preservation:** Maintaining the difference between a possible/suspected condition and a confirmed one.
- **Critical omission:** Failure to include an important fact that should be present in the summary.
- **ROUGE:** Lexical-overlap evaluation family.
- **BERTScore:** Semantic-similarity metric based on contextual representations.
- **FactCC:** Factual-consistency approach referenced in the slides for support/contradiction prediction and evidence identification.
- **AlignScore:** Alignment-based source-support evaluation metric referenced in the slides.
- **MEDAL:** Model-agnostic post-processing framework for hallucination detection/correction in clinical summarization, as described in the revised PPT.

---

## 12. Consolidated reference list

The following records reflect the citation information shown in the revised PPT. Verify each item against its official proceedings, publisher, or resource page before final submission; some slides do not provide complete metadata or direct URLs.

1. Lu, Q., Dou, D., & Nguyen, T. (2022). **ClinicalT5: A Generative Language Model for Clinical Text.** Findings of EMNLP.
2. Johnson, A. E. W., et al. (2023). **MIMIC-IV, a freely accessible electronic health record dataset.** *Scientific Data*.
3. **A Dataset and Benchmark for Hospital Course Summarization with Adapted Large Language Models.** (2025). Full author and venue details need verification.
4. **Clinical-T5: Large Language Models Built Using MIMIC Clinical Text.** PhysioNet resource (2023, as listed in the slides). Exact resource metadata needs verification.
5. Li, S., et al. (2024). **Better Late Than Never: Model-Agnostic Hallucination Post-Processing Framework Towards Clinical Text Summarization.** Findings of ACL.
6. Kryscinski, W., et al. (2020). **Evaluating the Factual Consistency of Abstractive Text Summarization.** EMNLP.
7. Nan, F., et al. (2021). **Improving Factual Consistency of Abstractive Text Summarization via Question Answering.** ACL-IJCNLP.
8. Zhu, C., et al. (2021). **Enhancing Factual Consistency of Abstractive Summarization.** NAACL-HLT.
9. Zha, Y., et al. (2023). **AlignScore: Evaluating Factual Consistency with a Unified Alignment Function.** ACL.
10. Luo, Z., Xie, Q., & Ananiadou, S. (2024). **Factual consistency evaluation of summarization in the Era of large language models.** *Expert Systems with Applications*.

---

## 13. Quick summary

The current proposal is a text-only clinical summarization system using MIMIC-IV-Note and ClinicalT5. Its distinguishing component is a post-generation verification process: split the draft into claims, connect claims to source evidence, check support and contradiction, preserve negation and uncertainty, and revise or remove unsupported claims before finalizing the summary. Evaluation combines lexical overlap (ROUGE), optional semantic similarity (BERTScore), factual-consistency methods (AlignScore or FactCC-style checks), and targeted manual error analysis. The original PDF includes OCR/CV and MIMIC-III/MIMIC-IV together; these were removed from the revised proposal's scope.
