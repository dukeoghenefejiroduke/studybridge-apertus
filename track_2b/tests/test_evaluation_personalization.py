from app.evaluation import EvaluationEngine


class FakeTutor:
    def answer_question(self, query):
        answers = {
            "What do cross-attention mechanisms do?":
                "They align visual regions with descriptive tokens.",
            "How is student mastery tracked?":
                "Bayesian Knowledge Tracing estimates learner mastery.",
            "Why is grounding important?":
                "Grounding can prevent hallucinations using retrieved evidence.",
        }

        return {
            "answer": answers.get(query, ""),
            "supported": query in answers,
            "citations": [],
        }


def test_evaluation_includes_personalization_report():
    engine = EvaluationEngine(None, FakeTutor())

    report = engine.run_evaluation()

    assert "personalization_evaluation" in report

    personalization = report["personalization_evaluation"]

    assert personalization["sessions_per_student"] == 3
    assert "grounding_focus" in personalization["profiles"]
    assert "learner_modeling_focus" in personalization["profiles"]


def test_personalization_report_contains_mastery_and_repetition_metrics():
    engine = EvaluationEngine(None, FakeTutor())

    report = engine.run_evaluation()
    profiles = report["personalization_evaluation"]["profiles"]

    for profile in profiles.values():
        assert profile["initial_mastery"]
        assert profile["final_mastery"]
        assert profile["mastery_gain"]
        assert profile["repetition_rate_percentage"] == 66.7


def test_weak_topic_consistency_is_reported():
    engine = EvaluationEngine(None, FakeTutor())

    report = engine.run_evaluation()

    consistency = report["personalization_evaluation"][
        "weak_topic_consistency"
    ]

    assert consistency["total"] == 2
    assert consistency["passed"] == 2
    assert consistency["percentage"] == 100.0


def test_existing_tutoring_benchmark_is_preserved():
    engine = EvaluationEngine(None, FakeTutor())

    report = engine.run_evaluation()

    assert report["total_test_cases"] == 3
    assert report["passed"] == 3
    assert report["accuracy_percentage"] == 100.0
    assert report["metrics"]["grounding_score"] == 1.0
