"""Safe in-memory decoding for uploaded report images."""

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


def decode_report_image(content: bytes) -> Image.Image:
    """Validate and decode one report image without writing it to disk."""
    if not content:
        raise ValueError("The uploaded file is empty.")
    if len(content) > MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds the 10 MB upload limit.")

    try:
        with Image.open(BytesIO(content)) as source:
            if source.format not in SUPPORTED_FORMATS:
                raise ValueError("Use a PNG, JPEG, or WebP image.")
            if getattr(source, "n_frames", 1) != 1:
                raise ValueError("Animated or multi-frame images are not supported.")
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions exceed the 25 megapixel limit.")

            source.load()
            oriented = ImageOps.exif_transpose(source)
            return oriented.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("The uploaded file is not a readable report image.") from error