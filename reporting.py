from __future__ import annotations

from datetime import datetime

import pandas as pd

from .analytics import ValidationSummary


def build_report_text(df: pd.DataFrame, summary: ValidationSummary) -> str:
    start_date = datetime.now().strftime("%Y-%m-%d")
    return f"""# Defensible TAR Validation Report

Generated: {start_date}

## Scope
This demo simulates an eDiscovery analytics advisor workflow for a high-stakes matter. It combines transparent scoring, QC sampling, privilege escalation, and validation reporting.

## Summary Metrics
- Documents analyzed: {len(df)}
- Relevant-document prevalence: {summary.prevalence:.2%}
- Precision at active cutoff: {summary.precision_at_threshold:.2%}
- Recall at active cutoff: {summary.recall_at_threshold:.2%}
- Elusion rate: {summary.elusion_rate:.2%}
- Privilege escalation rate: {summary.privileged_rate:.2%}
- Recommended cutoff based on weighted precision/recall: {summary.recommended_cutoff:.2f}

## Defensibility Notes
- Transparent scoring factors are exposed in code and can be explained to counsel.
- QC sampling emphasizes low-scoring but conceptually similar items to reduce missed relevant documents.
- Privilege flags are isolated for elevated handling and separate review.
- The workflow is intended for portfolio demonstration and not legal advice.
"""
