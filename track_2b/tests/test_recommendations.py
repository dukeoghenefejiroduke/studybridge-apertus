from app.main import build_study_recommendations


class FakeRetrievalEngine:
    """Provides predictable search results for isolated tests."""

    def __init__(self, results=None):
        self.results = results or []
        self.queries = []

    def search(self, query, top_k=3):
        self.queries.append((query, top_k))
        return self.results[:top_k]


def test_low_mastery_topic_is_prioritized(monkeypatch):
    import app.main as main

    monkeypatch.setattr(
        main,
        "retrieval_engine",
        FakeRetrievalEngine()
    )

    progress = {
        "Learner Modeling": {
            "mastery": 0.80,
            "sessions": 4,
            "status": "Proficient",
        },
        "Multimodal AI": {
            "mastery": 0.65,
            "sessions": 3,
            "status": "Developing",
        },
        "Grounding & RAG": {
            "mastery": 0.45,
            "sessions": 2,
            "status": "Needs Review",
        },
    }

    recommendations = build_study_recommendations(progress)

    assert len(recommendations) == 3
    assert recommendations[0]["topic"] == "Grounding & RAG"
    assert recommendations[0]["priority"] == "High"
    assert recommendations[1]["topic"] == "Multimodal AI"
    assert recommendations[1]["priority"] == "Medium"
    assert recommendations[2]["topic"] == "Learner Modeling"
    assert recommendations[2]["priority"] == "Maintain"


def test_recommendations_include_matching_materials(monkeypatch):
    import app.main as main

    material = {
        "title": "Grounding Lecture Notes",
        "source": "Lecture 3",
        "timestamp": "00:05:00",
        "score": 0.85,
    }

    engine = FakeRetrievalEngine([material])
    monkeypatch.setattr(main, "retrieval_engine", engine)

    progress = {
        "Grounding & RAG": {
            "mastery": 0.40,
            "sessions": 2,
            "status": "Needs Review",
        }
    }

    recommendations = build_study_recommendations(progress)

    assert recommendations[0]["materials"][0]["title"] == (
        "Grounding Lecture Notes"
    )
    assert recommendations[0]["materials"][0]["source"] == "Lecture 3"
    assert engine.queries


def test_recommendations_handle_no_matching_materials(monkeypatch):
    import app.main as main

    monkeypatch.setattr(
        main,
        "retrieval_engine",
        FakeRetrievalEngine()
    )

    progress = {
        "Grounding & RAG": {
            "mastery": 0.45,
            "sessions": 2,
            "status": "Needs Review",
        }
    }

    recommendations = build_study_recommendations(progress)

    assert len(recommendations) == 1
    assert recommendations[0]["materials"] == []
    assert recommendations[0]["action"]


def test_mastery_percentages_are_bounded(monkeypatch):
    import app.main as main

    monkeypatch.setattr(
        main,
        "retrieval_engine",
        FakeRetrievalEngine()
    )

    progress = {
        "Topic Above Range": {
            "mastery": 1.5,
            "sessions": 1,
            "status": "Proficient",
        },
        "Topic Below Range": {
            "mastery": -0.5,
            "sessions": 1,
            "status": "Needs Review",
        },
    }

    recommendations = build_study_recommendations(progress)
    by_topic = {item["topic"]: item for item in recommendations}

    assert by_topic["Topic Above Range"]["mastery_percentage"] == 100
    assert by_topic["Topic Below Range"]["mastery_percentage"] == 0
