from __future__ import annotations

import streamlit as st

from src.eltemate_advisor_demo.analytics import (
    classify_documents,
    compute_validation_summary,
    dashboard_metrics,
    issue_breakdown,
    qc_sample,
)
from src.eltemate_advisor_demo.data import load_demo_data
from src.eltemate_advisor_demo.reporting import build_report_text

st.set_page_config(page_title="ELTEMATE Advisor Demo", layout="wide")

st.title("ELTEMATE Advanced Client Data Solutions Advisor Demo")
st.caption(
    "Portfolio project inspired by the responsibilities of an Advanced Client Data Solutions "
    "Technology and Analytics Advisor: defensible analytics, TAR validation, workflow oversight, "
    "status reporting, and issue escalation."
)

with st.sidebar:
    st.header("Workflow Controls")
    threshold = st.slider("Relevance threshold", min_value=0.40, max_value=0.85, value=0.68, step=0.01)
    qc_count = st.slider("QC sample size", min_value=10, max_value=75, value=25, step=5)
    st.markdown("---")
    st.markdown(
        "**Why this fits the role**  \n"
        "• TAR / validation logic  \n"
        "• Defensible documentation  \n"
        "• Matter-level reporting  \n"
        "• Privilege escalation  \n"
        "• Cross-functional communication"
    )

raw_df = load_demo_data()
scored_df = classify_documents(raw_df)
summary = compute_validation_summary(scored_df, threshold=threshold)
metrics = dashboard_metrics(scored_df)
qc_df = qc_sample(scored_df, sample_size=qc_count)
issue_df = issue_breakdown(scored_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Documents", metrics["documents"])
col2.metric("Prioritize Review", metrics["prioritized"])
col3.metric("Privilege Review", metrics["privilege_review"])
col4.metric("QC / Defer Pool", metrics["sample_qc"] + metrics["deferred"])

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg Relevance", metrics["avg_relevance"])
col6.metric("Avg Privilege", metrics["avg_privilege"])
col7.metric("Precision", f"{summary.precision_at_threshold:.1%}")
col8.metric("Recall", f"{summary.recall_at_threshold:.1%}")

st.subheader("Matter Dashboard")
st.dataframe(issue_df, use_container_width=True, hide_index=True)

st.subheader("Review Queue")
queue_cols = [
    "document_id",
    "matter_name",
    "custodian",
    "relevance_score",
    "privilege_score",
    "recommended_action",
    "issue_antitrust",
    "issue_bribery",
    "issue_hr",
    "issue_pricing",
]
st.dataframe(
    scored_df.sort_values(["recommended_action", "relevance_score"], ascending=[True, False])[queue_cols],
    use_container_width=True,
    hide_index=True,
)

st.subheader("QC Sampling Recommendations")
st.dataframe(qc_df[queue_cols], use_container_width=True, hide_index=True)

st.subheader("Defensibility Report")
report_text = build_report_text(scored_df, summary)
st.download_button(
    "Download report",
    data=report_text,
    file_name="defensible_tar_validation_report.md",
    mime="text/markdown",
)
st.code(report_text, language="markdown")
