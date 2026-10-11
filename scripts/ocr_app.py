"""Local Streamlit interface for uploading and reviewing report OCR."""

import hashlib

import streamlit as st

from clinical_note_summarization.ocr.engine import (
    OCRRegion,
    create_ocr_engine,
    recognize_regions,
)
from clinical_note_summarization.ocr.image import decode_report_image


@st.cache_resource
def get_ocr_engine():
    return create_ocr_engine()


st.set_page_config(page_title="Report OCR Review", page_icon="R", layout="centered")
st.title("Medical Report OCR")
st.caption("Local image-to-text prototype. It does not interpret medical images or provide clinical advice.")
st.info("Uploaded files are processed in memory by this local app and are not saved by the application.")

uploaded_file = st.file_uploader(
    "Choose one report page",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
)

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    image_id = hashlib.sha256(image_bytes).hexdigest()[:16]

    try:
        report_image = decode_report_image(image_bytes)
    except ValueError as error:
        st.error(str(error))
    else:
        st.image(report_image, caption=uploaded_file.name, use_container_width=True)
        if st.button("Extract text", type="primary", key=f"extract-{image_id}"):
            try:
                regions = recognize_regions(report_image, get_ocr_engine())
                st.session_state[f"regions-{image_id}"] = regions
            except Exception as error:
                st.error("OCR could not process this image.")
                with st.expander("Technical details"):
                    st.code(str(error))

        regions: list[OCRRegion] | None = st.session_state.get(f"regions-{image_id}")
        if regions is not None:
            if regions:
                initial_text = "\n".join(region.text for region in regions)
                st.subheader("Review extracted text")
                st.caption("Check names, numbers, units, dates, medication details, and negation against the image.")
                st.text_area(
                    "OCR text (editable)",
                    value=initial_text,
                    height=260,
                    key=f"reviewed-text-{image_id}",
                )
                with st.expander("Recognition confidence by region"):
                    for region in regions:
                        st.write(f"{region.confidence:.1%}  {region.text}")
                    st.caption("OCR confidence indicates recognition confidence, not clinical certainty.")
            else:
                st.warning("No text was detected. Try a clearer or higher-resolution image.")