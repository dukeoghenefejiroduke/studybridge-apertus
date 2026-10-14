from app.personalization_evaluation import simulate_student_profiles


def test_simulation_reports_two_different_student_profiles():
    report = simulate_student_profiles(sessions=3)
    profiles = report["profiles"]

    assert "grounding_focus" in profiles
    assert "learner_modeling_focus" in profiles
    assert profiles["grounding_focus"]["weakest_topic"] == "Grounding & RAG"
    assert profiles["learner_modeling_focus"]["weakest_topic"] == "Learner Modeling"


def test_simulation_reports_mastery_changes_across_sessions():
    report = simulate_student_profiles(sessions=3)

    for profile in report["profiles"].values():
        assert len(profile["sessions"]) == 3
        assert profile["initial_mastery"]
        assert profile["final_mastery"]

        for topic, initial_value in profile["initial_mastery"].items():
            expected_gain = round(
                profile["final_mastery"][topic] - initial_value, 2
            )
            assert profile["mastery_gain"][topic] == expected_gain


def test_simulation_measures_question_repetition():
    report = simulate_student_profiles(sessions=3)

    for profile in report["profiles"].values():
        assert profile["question_exposures"] == 9
        assert profile["unique_questions"] == 3
        assert profile["repeated_question_exposures"] == 6
        assert profile["repetition_rate_percentage"] == 66.7


def test_simulation_rejects_invalid_session_count():
    import pytest

    with pytest.raises(ValueError):
        simulate_student_profiles(sessions=0)


def test_simulation_does_not_modify_real_progress_file(tmp_path):
    from app.learner_model import LearnerModel

    real_model = LearnerModel(data_dir=str(tmp_path / "real_progress"))
    before = {
        topic: dict(info)
        for topic, info in real_model.get_progress().items()
    }

    simulate_student_profiles(sessions=2)

    assert real_model.get_progress() == before


def test_recommendations_prioritize_each_students_weakest_topic(monkeypatch):
    import app.main as main

    class EmptyRetrieval:
        def search(self, query, top_k=3):
            return []

    monkeypatch.setattr(main, "retrieval_engine", EmptyRetrieval())

    report = simulate_student_profiles(sessions=3)

    for profile in report["profiles"].values():
        recommendations = main.build_study_recommendations(
            profile["final_mastery"]
            and {
                topic: {
                    "mastery": mastery,
                    "sessions": 3,
                    "status": (
                        "Needs Review" if mastery < 0.5
                        else "Developing" if mastery < 0.75
                        else "Proficient"
                    ),
                }
                for topic, mastery in profile["final_mastery"].items()
            }
        )

        assert recommendations
        assert recommendations[0]["topic"] == profile["weakest_topic"]
        assert recommendations[0]["priority"] == "High"
