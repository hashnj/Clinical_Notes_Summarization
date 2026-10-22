"""Optional local-only medical language-model generation."""

from __future__ import annotations

import importlib
from pathlib import Path


class LocalMedicalGenerator:
    """Run BioGPT from a local checkpoint; no note text is sent to an API."""

    def __init__(self, model_dir: str | Path):
        try:
            torch = importlib.import_module("torch")
            transformers = importlib.import_module("transformers")
        except ImportError as error:
            raise RuntimeError(
                "Install the optional model dependencies: "
                "`python -m pip install -e '.[models]'`."
            ) from error

        self._torch = torch
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(
            model_dir, local_files_only=True
        )
        self._model = transformers.AutoModelForCausalLM.from_pretrained(
            model_dir, local_files_only=True
        )
        self._model.eval()

    def summarize(self, text: str, max_new_tokens: int = 96) -> str:
        """Generate locally from a prompt; callers must review output clinically."""
        if not text.strip():
            raise ValueError("Cannot summarize empty text.")
        prompt = f"Summarize this clinical note:\n{text}\nSummary:"
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True)
        with self._torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        return self._tokenizer.decode(output[0], skip_special_tokens=True).split("Summary:", 1)[-1].strip()
