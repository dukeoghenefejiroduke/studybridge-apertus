import json

import pytest

from app.assessment import AssessmentEngine


def test_question_bank_has_twelve_questions_and_three_topics(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))
    questions = engine.get_questions()

    assert len(questions) == 12
    assert {q["topic"] for q in questions} == {
        "Multimodal AI",
        "Learner Modeling",
        "Grounding & RAG",
    }


def test_public_questions_hide_answers_and_include_metadata(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    for question in engine.get_questions():
        assert "correct_answer" not in question
        assert "explanation" not in question
        assert question["difficulty"] in {"easy", "medium", "hard"}
        assert "source_reference" in question
        assert question["source_status"] == "unlinked"


def test_legacy_three_question_scoring_still_works(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    result = engine.evaluate_quiz({
        "q1": "B",
        "q2": "B",
        "q3": "B",
    })

    assert result["score"] == 3
    assert result["total"] == 3
    assert result["percentage"] == 100.0


def test_missing_answers_evaluate_full_bank(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    result = engine.evaluate_quiz({})

    assert result["total"] == 12
    assert result["score"] == 0
    assert all(not item["correct"] for item in result["feedback"])


def test_adaptive_selection_returns_three_distinct_questions(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    questions = engine.select_questions(
        progress={
            "Multimodal AI": {"mastery": 0.8},
            "Learner Modeling": {"mastery": 0.7},
            "Grounding & RAG": {"mastery": 0.2},
        },
        limit=3,
    )

    assert len(questions) == 3
    assert len({q["id"] for q in questions}) == 3
    assert len({q["topic"] for q in questions}) == 3


def test_seen_questions_are_deprioritized(tmp_path):
    history_file = tmp_path / "history.json"
    engine = AssessmentEngine(str(history_file))

    first = engine.select_questions(limit=3)
    first_ids = [q["id"] for q in first]

    engine.record_questions_seen(first_ids)

    second = engine.select_questions(limit=3)
    second_ids = {q["id"] for q in second}

    assert not second_ids.intersection(first_ids)


def test_question_history_is_persisted(tmp_path):
    history_file = tmp_path / "history.json"
    engine = AssessmentEngine(str(history_file))

    engine.record_questions_seen(["q1", "q2", "not-a-real-question"])

    data = json.loads(history_file.read_text())

    assert data["seen_question_ids"] == ["q1", "q2"]


def test_invalid_question_limit_is_rejected(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    with pytest.raises(ValueError):
        engine.select_questions(limit=0)

    with pytest.raises(ValueError):
        engine.select_questions(limit=True)


def test_feedback_contains_topic_difficulty_and_source_status(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))

    result = engine.evaluate_quiz({"q1": "B"})
    feedback = result["feedback"][0]

    assert feedback["question_id"] == "q1"
    assert feedback["topic"] == "Multimodal AI"
    assert feedback["difficulty"] == "medium"
    assert feedback["source_reference"] is None
    assert feedback["source_status"] == "unlinked"


def test_topic_filter_selection(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))
    questions = engine.select_questions(topic="Multimodal AI", limit=2)
    assert len(questions) == 2
    for q in questions:
        assert q["topic"] == "Multimodal AI"


def test_invalid_topic_scope_raises_error(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))
    with pytest.raises(ValueError):
        engine.select_questions(topic="Nonexistent Topic")


def test_empty_topic_scope_raises_error(tmp_path):
    engine = AssessmentEngine(str(tmp_path / "history.json"))
    with pytest.raises(ValueError):
        engine.select_questions(topic="   ")


def test_api_quiz_with_topic_filter():
    from app.main import app
    app.config["TESTING"] = True
    client = app.test_client()
    res = client.get("/api/quiz?topic=Learner Modeling")
    assert res.status_code == 200
    data = res.get_json()
    assert "questions" in data
    for q in data["questions"]:
        assert q["topic"] == "Learner Modeling"

    res_invalid = client.get("/api/quiz?topic=BadTopic")
    assert res_invalid.status_code == 400
