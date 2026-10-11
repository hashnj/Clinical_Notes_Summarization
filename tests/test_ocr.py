from io import BytesIO

import pytest
from PIL import Image

from clinical_note_summarization.ocr.engine import recognize_regions
from clinical_note_summarization.ocr.image import MAX_IMAGE_BYTES, decode_report_image


def make_png() -> bytes:
    image = Image.new("RGB", (32, 24), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_decode_report_image_returns_oriented_rgb_image():
    image = decode_report_image(make_png())

    assert image.mode == "RGB"
    assert image.size == (32, 24)


@pytest.mark.parametrize("content", [b"", b"not an image"])
def test_decode_report_image_rejects_empty_or_invalid_content(content: bytes):
    with pytest.raises(ValueError):
        decode_report_image(content)


def test_decode_report_image_rejects_oversized_upload():
    with pytest.raises(ValueError, match="10 MB"):
        decode_report_image(b"x" * (MAX_IMAGE_BYTES + 1))


def test_recognize_regions_normalizes_engine_output():
    class FakeEngine:
        def __call__(self, image: object) -> object:
            assert image.shape == (24, 32, 3)
            return FakeResult()

    class FakeResult:
        boxes = [[[1, 2], [20, 2], [20, 8], [1, 8]]]
        txts = ("Report text",)
        scores = (0.97,)

    regions = recognize_regions(decode_report_image(make_png()), FakeEngine())

    assert len(regions) == 1
    assert regions[0].text == "Report text"
    assert regions[0].confidence == pytest.approx(0.97)
    assert regions[0].bounds[0] == (1.0, 2.0)