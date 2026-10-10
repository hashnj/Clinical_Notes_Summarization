### Complete implementation workflow: Clinical Note Summarization Without Hallucination
Your project should be implemented as a clinical text summarization system that uses ClinicalT5 to generate summaries and a verification pipeline to detect and reduce unsupported clinical claims.
The important part is that you are not merely building a model that summarizes text. You are evaluating whether the generated summary remains faithful to the original clinical note, particularly for diagnoses, medications, negation, and uncertainty.
I'll break the implementation into phases, explain what you need to build in each phase, and show how all the components fit together.
1. What exactly are we building?
# PROJECT INPUT
A de-identified clinical note from MIMIC-IV's clinical-note resource.

# CORE SYSTEM
Clinical note preprocessing
Clean, select, and prepare the note


# ClinicalT5 summarization
Generate a draft summary


# Factuality verification
Check claims against the source note


Final summary + evaluation report
Summary, evidence, detected errors, and quality scores


The project will have two major outputs:
1. A working summarization application or research prototype.
2. An experimental evaluation showing whether your verification stage improves factual consistency compared with ordinary ClinicalT5 generation.
You do not need OCR, computer vision, or a separate image-processing pipeline for this version.
2. First, settle the dataset and model correctly
This is the most important implementation decision. There is a ready-made dataset for almost exactly your task, so you should not spend weeks creating training labels from scratch.









# Dataset: MIMIC-IV-Ext-BHC
Recommended
It contains approximately 270,000 clinical-note and brief-hospital-course summary pairs derived from MIMIC-IV-Note. The source note is the input; the brief hospital course is the reference summary. 

PhysioNet
+2



Dataset and access instructions












# Model: ClinicalT5
ClinicalT5 is the clinical-domain encoder-decoder model you will use for text generation. The released models were pretrained on clinical notes from both MIMIC-III and MIMIC-IV; the official model weights require credentialed access. 

PhysioNet
+1



# ClinicalT5 model resource



Two distinctions matter:
- Dataset scope: Your downstream experiments can use only MIMIC-IV-derived data, specifically MIMIC-IV-Ext-BHC.
- Model provenance: The official ClinicalT5 checkpoint was pretrained on a mixture of MIMIC-III and MIMIC-IV notes. If your professor means that no MIMIC-III data may be used anywhere, including pretraining, confirm this constraint before committing to that checkpoint.
Both the dataset and the released ClinicalT5 weights have access requirements. Complete PhysioNet credentialing, required training, and data-use agreements before planning around them. 

PhysioNet
+1



What will your dataset look like?
The prepared dataset contains these fields:
Column	Meaning
note_id	Unique note identifier
input	Clinical note with the brief hospital course section separated out
target	Reference brief hospital course summary
input_tokens	Token count of the input
target_tokens	Token count of the reference summary


PhysioNet


Your core training example will be:
INPUT — input
Patient history, presenting complaint, relevant examination findings, investigations, treatments, and discharge information.

ClinicalT5
Fine-tuned for hospital-course summarization


TARGET — target
A concise summary of the hospital course, written by the original clinical documentation author.

The target summary gives you a reference for supervised fine-tuning and evaluation. It does not automatically give you labels saying which individual statements are hallucinations; those need to be assessed separately.
3. Phase-by-phase implementation plan
I recommend implementing the project in eight phases, in this order.

Phase 1 — Dataset acquisition and exploration
Foundation
Tasks:
- Obtain access to MIMIC-IV-Ext-BHC and the required ClinicalT5 checkpoint.
- Load the dataset with pandas.
- Inspect column names, missing values, duplicates, token lengths, and sample notes.
- Check that each input excludes the reference brief hospital course section.
- Verify that the input and target correspond to the same note.
Deliverable: A dataset exploration notebook and a report describing the data, its quality, and its limitations.




Phase 2 — Preprocessing and data splitting
Tasks:
- Remove malformed or empty note-summary pairs.
- Normalize whitespace and formatting without removing clinically meaningful content.
- Inspect special tokens and de-identification placeholders.
- Create training, validation, and test partitions, grouped by patient rather than randomly splitting individual notes.
- Handle long inputs using section-aware selection or chunking.
Deliverable: A reproducible preprocessing script and saved dataset partitions.
Avoid blindly truncating every note to the first 512 tokens. ClinicalT5's supported input length must be checked, and the chosen approach must preserve important facts from long notes. 

PhysioNet
+1







Phase 3 — Establish a baseline summarizer
Before training anything, load the ClinicalT5 tokenizer and model, run inference on a small number of notes, and save the outputs.
Tasks:
- Verify that the checkpoint and tokenizer load correctly.
- Generate summaries from unseen notes.
- Inspect output quality, length, truncation, repetitions, and missing information.
- Record initial ROUGE and other applicable evaluation metrics.
Deliverable: A working baseline that takes a clinical note and returns a draft summary.
This phase gives you a fallback if fine-tuning becomes difficult.




Phase 4 — Fine-tune ClinicalT5
Train the model to map input to target.
Tasks:
- Begin with a manageable subset of the training data.
- Use teacher-forced sequence-to-sequence training with the reference summary as the target.
- Monitor training loss and validation loss.
- Save checkpoints and use early stopping.
- Adjust learning rate, batch size, gradient accumulation, and sequence lengths to your available GPU memory.
- Compare fine-tuned output against the original baseline.
Deliverable: A fine-tuned ClinicalT5 checkpoint and a training log.
Start small, establish a reproducible run, and scale up only after the entire training and evaluation pipeline works.




Phase 5 — Implement factuality verification
This is the main research component beyond ordinary summarization.
For each generated summary:
- Split it into sentences or individual factual claims.
- Retrieve the most relevant evidence sentences from the original note.
- Check whether the evidence supports, contradicts, or fails to establish each claim.
- Preserve supported claims, revise or remove unsupported claims where possible, and flag unresolved cases.
- Re-check revised claims against the original note.
Deliverable: A verification module that returns the summary, evidence for each claim, and detected factuality issues.
Start with a simple retrieval-plus-entailment pipeline. Do not assume a generic entailment model is clinically reliable without evaluating it on clinical examples.




Phase 6 — Run experiments and evaluate
Compare at least three conditions:
1. Original ClinicalT5 baseline.
2. Fine-tuned ClinicalT5.
3. Fine-tuned ClinicalT5 with factuality verification.
Measure summary quality, important-fact preservation, unsupported claims, contradictions, and processing time.
Deliverable: A reproducible evaluation script, metrics table, error analysis, and plots for the report.




Phase 7 — Build a demonstration interface
Create a small web interface where a researcher can select or load an authorized test note, generate a summary, inspect evidence, and compare the verified result with the draft.
Deliverable: A working demonstration application.
This is a presentation layer, not the central research contribution.




Phase 8 — Error analysis, reproducibility, and final report
Tasks:
- Analyze hallucinations, contradictions, omissions, negation errors, medication errors, and uncertainty changes.
- Document examples where verification helps and where it fails.
- Record model checkpoints, hyperparameters, data partitions, and random seeds.
- Document limitations and the restrictions on clinical use.
Deliverable: The final experimental report, reproducible code, results, and demonstration.



4. The factuality verification module in detail
This is the part I would spend the most research effort on. Simply fine-tuning ClinicalT5 is not enough to make the project distinctive.
Proposed verification algorithm
A. Generated summary
Example: “The patient was treated with antibiotics.”


B. Claim extraction
Identify each independent clinical assertion


C. Evidence retrieval
Find the most relevant sentences in the original note


D. Entailment and contradiction checks
Classify evidence as supporting, contradicting, or inconclusive

Supported
Keep claim


Contradicted
Revise or remove


Uncertain
Flag for review




The output should include both the final summary and an evidence report.
For example, if the generated summary says a patient has diabetes but the note states that the patient has no history of diabetes, the verification stage should identify the contradiction. It must not simply mark the sentence as correct because it contains the same medical term.
What do you actually need to code?
Component	Implementation
Claim segmentation	Sentence splitting, with optional splitting of compound claims
Evidence retrieval	TF-IDF/BM25 initially; optionally sentence embeddings
Support/contradiction detection	Natural language inference model
Verification policy	Thresholds for supported, contradicted, and uncertain claims
Claim correction	Conservative rule-based removal or revision; optional second model pass
Evidence report	Claim, source sentence, classification, confidence, and action
A useful initial implementation is a retrieve-then-verify pipeline. You do not need to train a second large model from scratch.
One important caveat: deleting every sentence classified as unsupported could remove valid information when the relevant evidence is elsewhere in a long note. For that reason, evidence retrieval must consider multiple relevant source sentences, and low-confidence cases should be flagged rather than automatically deleted.
Also, don't claim that the system eliminates hallucinations. Your research question is whether this approach reduces them while retaining important clinical information.
5. Experimental design: how to prove the project works
Your experiments should be designed before training, rather than choosing metrics after seeing the results.
Models and system variants
Variant	Purpose
A. Original ClinicalT5	Establishes the pretrained baseline
B. Fine-tuned ClinicalT5	Measures improvement from task-specific training
C. Fine-tuned ClinicalT5 + verification	Tests your main research contribution
Use the same held-out test set for all three. Fix the generation settings and use identical test inputs to make the comparisons fair.
Evaluation metrics

Summary quality
- ROUGE-1, ROUGE-2, ROUGE-L
- BERTScore, if computational resources permit
These measure overlap or semantic similarity with the reference. They cannot establish clinical correctness on their own.




Factual consistency
- Unsupported-claim rate
- Contradiction rate
- Percentage of claims with identifiable source evidence
- AlignScore or a FactCC-style metric as an additional automated measure
These metrics need validation on clinical examples. A generic factuality score is not a substitute for clinical review.




Clinical information preservation
- Important diagnosis and treatment coverage
- Negation preservation
- Medication and dosage accuracy where applicable
- Preservation of uncertainty and temporal information
Measure these using an explicit annotation rubric on a manually reviewed sample.




Efficiency
- Inference time per note
- Verification time per note
- GPU memory usage
- Percentage of claims flagged for review
This establishes the computational cost of adding verification.



Your primary result should answer:
Does adding evidence-based verification reduce unsupported or contradictory claims compared with fine-tuned ClinicalT5 alone, without substantially reducing summary completeness?

That question makes the project measurable and research-oriented.
Manual evaluation
Set aside a manageable sample of test cases for manual inspection. For each case, assess:
- Whether the summary is supported by the source.
- Whether a clinically important fact was omitted.
- Whether a negation, medication, or temporal detail changed.
- Whether the verifier correctly identified the error.
- Whether correction introduced a new error.
If possible, have a qualified clinical reviewer assess a subset. If that is not possible, clearly label the evaluation as researcher annotation rather than clinical validation.
6. Recommended technology stack
Keep the stack simple. Most of the research work will happen in Python and Jupyter notebooks.
Component	Recommended technology
Language	Python
Dataset processing	pandas, NumPy, regex
Model and training	PyTorch, Hugging Face Transformers
Tokenization	ClinicalT5 tokenizer
Training optimization	Hugging Face Trainer, optional PEFT/LoRA
Evidence retrieval	BM25 or TF-IDF; optionally sentence-transformers
Factuality checking	NLI model, optionally AlignScore or FactCC-style scoring
Metrics	ROUGE, BERTScore, custom factuality metrics
Experiment tracking	CSV logs initially; optionally Weights & Biases
Demonstration interface	Streamlit
Version control	Git and GitHub, without committing restricted data or model weights
You do not need a React frontend, backend API, or database for the initial research implementation. A Streamlit application is enough to demonstrate the complete pipeline. Add a more elaborate interface only after the model and experiments work.
7. Suggested project folder structure
Organize the project from the beginning so that preprocessing, model training, verification, and evaluation remain separate.
clinical-note-summarization/

data/
Dataset access scripts and generated splits; keep restricted data out of Git.


notebooks/
Exploration, baseline tests, and error analysis.


src/data/
Loading, preprocessing, validation, and patient-level splitting.


src/models/
ClinicalT5 loading, fine-tuning, and inference.


src/verification/
Claim segmentation, evidence retrieval, entailment, and correction.


src/evaluation/
ROUGE, BERTScore, factuality metrics, and clinical error analysis.


app/
Streamlit demonstration interface.


configs/
Model settings, sequence lengths, and experiment parameters.


outputs/
Metrics, sample predictions, logs, and plots.


tests/
Unit tests for data splits, truncation, verification, and evaluation.


requirements.txt
Python dependencies.


README.md
Setup, reproduction instructions, dataset access, and limitations.




Keep raw clinical notes, model checkpoints, and other restricted materials out of public repositories. Follow PhysioNet's applicable terms for derived data and models as well.
8. What should you implement first?
Do not start by downloading the entire dataset and immediately training a model. Use these milestones to reduce the risk of getting stuck.
Implementation checklist
0 of 18 tasks



Milestone 1 — Access and inspect
Days 1–3

0/3

[ ] Confirm access to the BHC dataset and ClinicalT5 checkpoint
[ ] Load a small sample and inspect input/target pairs
[ ] Confirm tokenizer, hardware, and context limits


Milestone 2 — Baseline generation
Days 4–6

0/3

[ ] Run ClinicalT5 inference
[ ] Save generated summaries
[ ] Implement baseline evaluation


Milestone 3 — Fine-tuning
Week 2

0/3

[ ] Build patient-level data splits
[ ] Train on a small subset
[ ] Evaluate and save the best checkpoint


Milestone 4 — Verification module
Weeks 3–4

0/3

[ ] Implement claim segmentation and evidence retrieval
[ ] Integrate an NLI-based support checker
[ ] Add conservative correction and evidence reporting


Milestone 5 — Experiments
Week 5

0/3

[ ] Compare the three system variants
[ ] Calculate factuality and quality metrics
[ ] Manually inspect errors and ablation results


Milestone 6 — Demonstration and report
Week 6

0/3

[ ] Build the Streamlit interface
[ ] Document results and limitations
[ ] Prepare reproducible code and presentation

 Copy implementation plan
These estimates assume the necessary access and a suitable GPU are available. Fine-tuning or troubleshooting restricted model access can take longer than expected.
9. Risks you should resolve early
Model access
ClinicalT5's official weights require credentialed access. Confirm that you can actually obtain the checkpoint before making it a hard dependency. If access is unavailable, establish a T5-family fallback and document the change.


Long clinical notes
Inputs may exceed the model's supported sequence length. Compare section selection, chunking, and hierarchical summarization on a small sample before choosing a method. Record how much source content is retained.


Verifier reliability
A general-purpose NLI model can misunderstand clinical negation, abbreviations, and uncertainty. Validate its classifications on manually reviewed examples before relying on them.


Data leakage
Notes from the same patient should not appear in both training and test sets. Otherwise, your evaluation may overestimate generalization.



10. What is the minimum viable research contribution?
If time or compute is limited, prioritize these components:
- [ ] A working ClinicalT5 baseline.
- [ ] Fine-tuning on MIMIC-IV-derived note-summary pairs.
- [ ] A retrieval-plus-entailment verification module.
- [ ] A comparison between baseline, fine-tuned, and verified summaries.
- [ ] Evaluation of factual errors and preservation of important information.
- [ ] A small demonstration interface and reproducible report.
Avoid adding unrelated features such as OCR, disease prediction, a chatbot, or a complex user-management system. They will increase the workload without directly answering your research question.
My recommended next step: first verify dataset access, model access, and the available GPU. Then build the data-loading and baseline-inference notebook. Once those two steps work, the rest of the project can be implemented incrementally, with each phase producing a measurable result.
