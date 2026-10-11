"""Local OCR adapter that retains recognized text and region confidence."""

from dataclasses import dataclass
from typing import Protocol

from PIL import Image


class OCRBackend(Protocol):
    def __call__(self, image: object) -> object: ...


@dataclass(frozen=True)
class OCRRegion:
    text: str
    confidence: float
    bounds: tuple[tuple[float, float], ...]


def create_ocr_engine() -> OCRBackend:
    """Create the optional RapidOCR CPU engine."""
    try:
        from rapidocr import RapidOCR
    except ImportError as error:
        raise RuntimeError(
            "OCR dependencies are missing. Install the app extra with "
            "`python -m pip install -e '.[app]'`."
        ) from error

    return RapidOCR()


def recognize_regions(image: Image.Image, engine: OCRBackend) -> list[OCRRegion]:
    """Run OCR on an RGB image and normalize detected text regions."""
    try:
        import numpy as np
    except ImportError as error:
        raise RuntimeError("NumPy is required by the OCR app extra.") from error

    result = engine(np.asarray(image.convert("RGB")))
    if result is None:
        return []

    boxes = getattr(result, "boxes", None)
    texts = getattr(result, "txts", None)
    confidences = getattr(result, "scores", None)
    if boxes is None or texts is None or confidences is None:
        raise ValueError("The OCR engine returned an invalid result object.")

    regions: list[OCRRegion] = []
    try:
        detections = zip(boxes, texts, confidences, strict=True)
        for polygon, text, confidence in detections:
            bounds = tuple((float(point[0]), float(point[1])) for point in polygon)
            normalized_text = str(text).strip()
            normalized_confidence = float(confidence)

            if normalized_text:
                regions.append(
                    OCRRegion(
                        text=normalized_text,
                        confidence=normalized_confidence,
                        bounds=bounds,
                    )
                )
    except (TypeError, ValueError, IndexError) as error:
        raise ValueError("The OCR engine returned an invalid text region.") from error

    return regions