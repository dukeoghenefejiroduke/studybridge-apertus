"""
Unit tests for evaluation engine and benchmark reporting in StudyBridge AI.
"""

import pytest
from app.evaluation import EvaluationEngine
from app.ingestion import IngestionManager
from app.retrieval import RetrievalEngine
from app.tutor import TutorEngine

def test_evaluation_engine_metrics_structure():
    ingestion = IngestionManager(data_dir="data/test_eval_proc")
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)
    engine = EvaluationEngine(retrieval, tutor)

    report = engine.run_evaluation()
    assert "total_test_cases" in report
    assert "passed" in report
    assert "accuracy_percentage" in report
    assert "metrics" in report
    assert "grounding_score" in report["metrics"]
    assert "personalization_evaluation" in report
