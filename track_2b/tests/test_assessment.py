"""
Unit tests for Assessment engine in StudyBridge AI.
"""

import pytest
from app.assessment import AssessmentEngine
from app.main import app

def test_assessment_questions():
    engine = AssessmentEngine()
    questions = engine.get_questions()
    assert len(questions) > 0
    assert "prompt" in questions[0]
    assert "options" in questions[0]

def test_assessment_evaluation():
    engine = AssessmentEngine()
    # Mock answers (assuming q1='B', q2='B', q3='B' are correct per assessment.py)
    answers = {
        "q1": "B",
        "q2": "B",
        "q3": "B"
    }
    result = engine.evaluate_quiz(answers)
    assert result["score"] == 3
    assert result["total"] == 3
    assert result["percentage"] == 100.0


def test_missing_answers_are_marked_incorrect():
    engine = AssessmentEngine()

    result = engine.evaluate_quiz({})

    assert result["score"] == 0
    assert result["total"] == len(engine.questions)
    assert result["percentage"] == 0.0
    assert all(not item["correct"] for item in result["feedback"])
    assert all(item["user_answer"] == "" for item in result["feedback"])


def test_answers_are_normalized():
    engine = AssessmentEngine()

    result = engine.evaluate_quiz({
        "q1": " b ",
        "q2": "B",
        "q3": "b"
    })

    assert result["score"] == 3
    assert result["percentage"] == 100.0


def test_invalid_answer_values_do_not_crash():
    engine = AssessmentEngine()

    result = engine.evaluate_quiz({
        "q1": None,
        "q2": 123,
        "q3": "INVALID"
    })

    assert result["score"] == 0
    assert all(item["user_answer"] == "" for item in result["feedback"])


def test_non_dictionary_answers_are_rejected():
    engine = AssessmentEngine()

    with pytest.raises(ValueError):
        engine.evaluate_quiz(["B", "B", "B"])


def test_all_quiz_questions_have_valid_mcq_type():
    engine = AssessmentEngine()

    for question in engine.get_questions():
        assert question["type"] == "mcq"
        assert len(question["options"]) == 4


def test_api_quiz_get_endpoint():
    app.config["TESTING"] = True
    client = app.test_client()
    res = client.get("/api/quiz")
    assert res.status_code == 200
    data = res.get_json()
    assert "questions" in data
    assert len(data["questions"]) == 3
    for q in data["questions"]:
        assert "correct_answer" not in q
        assert "explanation" not in q


def test_api_quiz_submit_endpoint_cases():
    app.config["TESTING"] = True
    client = app.test_client()

    # 1. Malformed / non-dict body
    res = client.post("/api/quiz/submit", json=["not", "a", "dict"])
    assert res.status_code == 400

    # 2. Missing answers dict
    res = client.post("/api/quiz/submit", json={"not_answers": {}})
    assert res.status_code == 400

    # 3. Valid submission
    res = client.post("/api/quiz/submit", json={"answers": {"q1": "B"}})
    assert res.status_code == 200
    data = res.get_json()
    assert "score" in data
    assert "feedback" in data

    # 4. Unknown question IDs and invalid answer choices
    res = client.post("/api/quiz/submit", json={"answers": {"fake_id": "B", "q1": "INVALID"}})
    assert res.status_code == 200
    data = res.get_json()
    assert data["score"] == 0


def test_api_quiz_topics_endpoint():
    app.config["TESTING"] = True
    client = app.test_client()
    res = client.get("/api/quiz/topics")
    assert res.status_code == 200
    data = res.get_json()
    assert "topics" in data
    assert len(data["topics"]) > 0
    assert "Multimodal AI" in data["topics"]
