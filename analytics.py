from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd


@dataclass
class ValidationSummary:
    prevalence: float
    precision_at_threshold: float
    recall_at_threshold: float
    elusion_rate: float
    privileged_rate: float
    recommended_cutoff: float


def classify_documents(df: pd.DataFrame) -> pd.DataFrame:
    """Create defensible, explainable scores for a TAR-like workflow.

    The scoring formula is intentionally transparent so it can be discussed in interviews.
    """
    result = df.copy()
    result["relevance_score"] = (
        0.45 * result["keyword_hit_rate"]
        + 0.20 * result["concept_similarity"]
        + 0.15 * (result["custodian_risk"] / 5)
        + 0.10 * result["email_thread_depth"].clip(0, 10) / 10
        + 0.10 * result["recency_weight"]
    ).round(4)

    result["privilege_score"] = (
        0.50 * result["privileged_terms_flag"]
        + 0.25 * result["outside_counsel_flag"]
        + 0.15 * result["work_product_flag"]
        + 0.10 * result["legal_hold_overlap"]
    ).round(4)

    result["recommended_action"] = np.select(
        [
            result["privilege_score"] >= 0.60,
            result["relevance_score"] >= 0.68,
            result["relevance_score"] >= 0.45,
        ],
        ["Privilege Review", "Prioritize Review", "Sample/QC"],
        default="Defer",
    )
    return result


def compute_validation_summary(df: pd.DataFrame, threshold: float = 0.68) -> ValidationSummary:
    relevant = df["ground_truth_relevant"] == 1
    predicted = df["relevance_score"] >= threshold

    tp = int((relevant & predicted).sum())
    fp = int((~relevant & predicted).sum())
    fn = int((relevant & ~predicted).sum())
    tn = int((~relevant & ~predicted).sum())

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    prevalence = relevant.mean()
    elusion = fn / (fn + tn) if (fn + tn) else 0.0
    privileged_rate = (df["privilege_score"] >= 0.60).mean()

    recommended_cutoff = recommend_cutoff(df)
    return ValidationSummary(
        prevalence=round(float(prevalence), 4),
        precision_at_threshold=round(float(precision), 4),
        recall_at_threshold=round(float(recall), 4),
        elusion_rate=round(float(elusion), 4),
        privileged_rate=round(float(privileged_rate), 4),
        recommended_cutoff=round(float(recommended_cutoff), 2),
    )


def recommend_cutoff(df: pd.DataFrame) -> float:
    candidate_thresholds = np.arange(0.40, 0.86, 0.02)
    best_threshold = 0.68
    best_score = -1.0

    for threshold in candidate_thresholds:
        relevant = df["ground_truth_relevant"] == 1
        predicted = df["relevance_score"] >= threshold
        tp = int((relevant & predicted).sum())
        fp = int((~relevant & predicted).sum())
        fn = int((relevant & ~predicted).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        score = (0.65 * precision) + (0.35 * recall)
        if score > best_score:
            best_score = score
            best_threshold = threshold

    return float(best_threshold)


def qc_sample(df: pd.DataFrame, sample_size: int = 25) -> pd.DataFrame:
    qc_pool = df[df["recommended_action"].isin(["Sample/QC", "Defer"])].copy()
    if qc_pool.empty:
        return df.head(0).copy()

    qc_pool["qc_weight"] = (
        0.60 * (1 - qc_pool["relevance_score"])
        + 0.25 * qc_pool["concept_similarity"]
        + 0.15 * qc_pool["legal_hold_overlap"]
    )
    qc_pool = qc_pool.sort_values(["qc_weight", "document_id"], ascending=[False, True])
    return qc_pool.head(sample_size).drop(columns=["qc_weight"])


def dashboard_metrics(df: pd.DataFrame) -> Dict[str, float]:
    return {
        "documents": int(len(df)),
        "prioritized": int((df["recommended_action"] == "Prioritize Review").sum()),
        "privilege_review": int((df["recommended_action"] == "Privilege Review").sum()),
        "sample_qc": int((df["recommended_action"] == "Sample/QC").sum()),
        "deferred": int((df["recommended_action"] == "Defer").sum()),
        "avg_relevance": round(float(df["relevance_score"].mean()), 3),
        "avg_privilege": round(float(df["privilege_score"].mean()), 3),
    }


def issue_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["issue_antitrust", "issue_bribery", "issue_hr", "issue_pricing"]
    labels = {
        "issue_antitrust": "Antitrust",
        "issue_bribery": "Bribery / FCPA",
        "issue_hr": "HR / Employment",
        "issue_pricing": "Pricing / Commercial",
    }
    data = []
    for col in cols:
        subset = df[df[col] == 1]
        data.append(
            {
                "issue": labels[col],
                "documents": int(len(subset)),
                "avg_relevance": round(float(subset["relevance_score"].mean()), 3) if len(subset) else 0.0,
                "avg_privilege": round(float(subset["privilege_score"].mean()), 3) if len(subset) else 0.0,
            }
        )
    return pd.DataFrame(data)
