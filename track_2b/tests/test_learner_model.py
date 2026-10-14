"""
Unit tests for Learner Model in StudyBridge AI.
"""

import pytest
import os
import json
from app.learner_model import LearnerModel

def test_learner_model_progress():
    model = LearnerModel(data_dir="data/test_processed")
    progress = model.get_progress()
    assert "Multimodal AI" in progress
    assert "mastery" in progress["Multimodal AI"]
    assert "status" in progress["Multimodal AI"]

def test_learner_model_update():
    model = LearnerModel(data_dir="data/test_processed")
    quiz_results = {
        "feedback": [
            {"topic": "Multimodal AI", "correct": True},
            {"topic": "Multimodal AI", "correct": True}
        ]
    }
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert updated["mastery"] > 0.0

def test_correct_answers_increase_mastery(tmp_path):
    model = LearnerModel(data_dir=str(tmp_path))
    model.progress["Multimodal AI"] = {"mastery": 0.50, "sessions": 1, "status": "Developing"}
    quiz_results = {
        "feedback": [
            {"topic": "Multimodal AI", "correct": True}
        ]
    }
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert updated["mastery"] > 0.50

def test_incorrect_answers_decrease_mastery(tmp_path):
    model = LearnerModel(data_dir=str(tmp_path))
    model.progress["Multimodal AI"] = {"mastery": 0.90, "sessions": 2, "status": "Proficient"}
    quiz_results = {
        "feedback": [
            {"topic": "Multimodal AI", "correct": False}
        ]
    }
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert updated["mastery"] < 0.90

def test_mastery_bounds_respected(tmp_path):
    model = LearnerModel(data_dir=str(tmp_path))
    model.progress["Multimodal AI"] = {"mastery": 1.0, "sessions": 1, "status": "Proficient"}
    # All correct when already 1.0
    quiz_results = {"feedback": [{"topic": "Multimodal AI", "correct": True}]}
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert updated["mastery"] <= 1.0

    model.progress["Multimodal AI"] = {"mastery": 0.0, "sessions": 1, "status": "Needs Review"}
    # All incorrect when already 0.0
    quiz_results = {"feedback": [{"topic": "Multimodal AI", "correct": False}]}
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert updated["mastery"] >= 0.0

def test_malformed_progress_file_handled_safely(tmp_path):
    progress_file = tmp_path / "learner_progress.json"
    progress_file.write_text("{invalid json content")
    model = LearnerModel(data_dir=str(tmp_path))
    progress = model.get_progress()
    assert "Multimodal AI" in progress

def test_learner_model_history_tracking(tmp_path):
    model = LearnerModel(data_dir=str(tmp_path))
    model.progress["Multimodal AI"] = {"mastery": 0.50, "sessions": 1, "status": "Developing", "history": [0.50]}
    quiz_results = {
        "feedback": [
            {"topic": "Multimodal AI", "correct": True}
        ]
    }
    updated = model.update_mastery("Multimodal AI", quiz_results)
    assert "history" in updated
    assert len(updated["history"]) >= 2
