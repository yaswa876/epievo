import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    parse_fasta,
    mutation_analysis,
    predict_epitopes,
    escape_score
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="EpiEvo Platform",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS STYLING
# -----------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 40px;
    font-weight: 700;
    color: #1f4e79;
}
.sub-title {
    font-size: 18px;
    color: #555;
}
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 30px;
}
.metric-box {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------
st.markdown(
    '<p class="main-title">EpiEvo</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Immune Escape and Epitope Evolution Prediction Platform</p>',
    unsafe_allow_html=True
)

st.divider()

# -----------------------------------
# SIDEBAR WORKFLOW
# -----------------------------------
st.sidebar.title("Workflow")

st.sidebar.info("""
Step 1: Upload FASTA  
Step 2: Mutation Analysis  
Step 3: Epitope Prediction  
Step 4: Escape Risk Calculation  
Step 5: Visualization
""")

uploaded_file = st.file_uploader(
    "Upload Multi-Strain FASTA File",
    type=["fasta", "fa"]
)

# -----------------------------------
# PROCESSING
# -----------------------------------
if uploaded_file:

    df = parse_fasta(uploaded_file)

    # SECTION 1 — SEQUENCES
    st.markdown(
        '<p class="section-title">Uploaded Sequences</p>',
        unsafe_allow_html=True
    )

    st.dataframe(df, use_container_width=True)

    # -----------------------------------
    # MUTATION ANALYSIS
    # -----------------------------------
    mut_df = mutation_analysis(df)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Strains", len(df))
    col2.metric("Protein Length", len(df.iloc[0]["sequence"]))
    col3.metric(
        "Avg Mutation Frequency",
        round(mut_df["Mutation_Frequency"].mean(), 3)
    )

    st.markdown(
        '<p class="section-title">Mutation Frequency Landscape</p>',
        unsafe_allow_html=True
    )

    heatmap = px.imshow(
        [mut_df["Mutation_Frequency"]],
        labels=dict(x="Position", y="", color="Frequency"),
        aspect="auto"
    )

    st.plotly_chart(heatmap, use_container_width=True)

    # -----------------------------------
    # EPITOPE PREDICTION
    # -----------------------------------
    ref_seq = df.iloc[0]["sequence"]
    epi_df = predict_epitopes(ref_seq)

    st.markdown(
        '<p class="section-title">Predicted Epitope Regions</p>',
        unsafe_allow_html=True
    )

    st.dataframe(
        epi_df.sort_values(
            "Epitope_Score",
            ascending=False
        ).head(25),
        use_container_width=True
    )

    # -----------------------------------
    # ESCAPE ANALYSIS
    # -----------------------------------
    esc_df = escape_score(mut_df, epi_df)

    st.markdown(
        '<p class="section-title">Immune Escape Risk Dashboard</p>',
        unsafe_allow_html=True
    )

    top_escape = esc_df.sort_values(
        "Escape_Score",
        ascending=False
    ).head(20)

    bar_fig = px.bar(
        top_escape,
        x="Peptide",
        y="Escape_Score",
        title="Top Escape-Prone Epitopes"
    )

    st.plotly_chart(bar_fig, use_container_width=True)

    st.dataframe(top_escape, use_container_width=True)

    # -----------------------------------
    # DOWNLOAD REPORTS
    # -----------------------------------
    st.markdown(
        '<p class="section-title">Export Results</p>',
        unsafe_allow_html=True
    )

    st.download_button(
        "Download Mutation Data",
        mut_df.to_csv(index=False),
        file_name="mutation_analysis.csv"
    )

    st.download_button(
        "Download Escape Scores",
        esc_df.to_csv(index=False),
        file_name="escape_scores.csv"
    )
