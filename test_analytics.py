from src.advisor_demo.analytics import classify_documents, compute_validation_summary
from src.advisor_demo.data import load_demo_data


def test_classify_documents_creates_expected_columns():
    df = classify_documents(load_demo_data())
    assert {"relevance_score", "privilege_score", "recommended_action"}.issubset(df.columns)


def test_validation_summary_has_reasonable_ranges():
    df = classify_documents(load_demo_data())
    summary = compute_validation_summary(df)
    assert 0 <= summary.precision_at_threshold <= 1
    assert 0 <= summary.recall_at_threshold <= 1
    assert 0 <= summary.elusion_rate <= 1
