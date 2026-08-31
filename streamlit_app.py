"""Streamlit page for ANALYSIS.md section 16 facet charts."""

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
PNG_DIR = ROOT / "output" / "png" / "analysis"

FIGURES = [
    {
        "title": "County",
        "file": "training_status_facet_county.png",
        "caption": (
            "One panel per county, sorted by not-sent share. "
            "Hiiumaa is highest (37.9%), Valgamaa lowest (10.3%)."
        ),
    },
    {
        "title": "Sex",
        "file": "training_status_facet_sex.png",
        "caption": (
            "Not sent is almost the same for women and men. "
            "Men have a higher not-participated share (4.2% vs 2.3%)."
        ),
    },
    {
        "title": "Age group",
        "file": "training_status_facet_age.png",
        "caption": (
            "Sorted by not sent. Age 55+ is first (25.9% not sent); "
            "other ages sit near the overall mix."
        ),
    },
    {
        "title": "Age group and sex",
        "file": "training_status_facet_age_sex.png",
        "caption": (
            "Women aged 55+ are the outlier: 31.2% not sent, "
            "versus 21.1% for men 55+."
        ),
    },
    {
        "title": "County and sex",
        "file": "training_status_facet_county_sex.png",
        "caption": (
            "Same county order as above. Non-participation is higher "
            "for men in Pärnumaa, Tartumaa, and Ida-Virumaa."
        ),
    },
    {
        "title": "County and age",
        "file": "training_status_facet_county_age.png",
        "caption": (
            "Age clusters inside each county. Small counties have thin "
            "age cells, so those bars move more."
        ),
    },
]

st.set_page_config(
    page_title="Training status comparison",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 880px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Faceted comparison of the three training statuses")
st.markdown(
    """
Unemployed people are split into **not sent**, **not participated**
(`jäi ära`, `keeldus`, `loobus`), and **participated** (`lõpetas` or
`katkestas`). Each chart uses the same colours, a shared 0–100% scale,
and dashed lines for the overall mix: not sent **21.4%**, not participated
**3.3%**, participated **75.3%**. Panels are sorted by not-sent share.
"""
)

for figure in FIGURES:
    path = PNG_DIR / figure["file"]
    st.subheader(figure["title"])
    if path.exists():
        st.image(str(path), use_container_width=True)
        st.caption(figure["caption"])
    else:
        st.warning(f"Figure not found: `{path.name}`. Run `python main.py` first.")
    st.divider()
