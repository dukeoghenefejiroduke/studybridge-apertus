"""
Deterministic personalization experiment for StudyBridge AI.

Uses isolated temporary storage so simulated students cannot overwrite
the real learner progress file.
"""

import tempfile

from app.assessment import AssessmentEngine
from app.learner_model import LearnerModel


def simulate_student_profiles(sessions=3):
    """Simulate students with different weaknesses across study sessions."""

    if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions < 1:
        raise ValueError("sessions must be a positive integer")

    profiles = {
        "grounding_focus": {
            "description": "Student struggling with Grounding & RAG",
            "answers": {"q1": "B", "q2": "B", "q3": "A"},
        },
        "learner_modeling_focus": {
            "description": "Student struggling with Learner Modeling",
            "answers": {"q1": "B", "q2": "A", "q3": "B"},
        },
    }

    engine = AssessmentEngine()
    all_questions = engine.get_questions()

    if not all_questions:
        raise ValueError("Cannot simulate learning without quiz questions")

    # Keep the experiment aligned with the app's three-question quiz.
    # Select one question from each topic so both simulated students are
    # assessed across the same topics in every session.
    questions_by_topic = {}
    for question in all_questions:
        questions_by_topic.setdefault(question["topic"], question)

    questions = list(questions_by_topic.values())[:3]
    question_ids = [question["id"] for question in questions]

    if not question_ids:
        raise ValueError("Cannot simulate learning without quiz questions")

    # The simulation profiles use fixed answers for q1, q2, and q3.
    # Restrict the simulated assessment to those same questions.
    questions = [
        question for question in questions
        if question["id"] in {"q1", "q2", "q3"}
    ]
    question_ids = [question["id"] for question in questions]

    if not question_ids:
        raise ValueError("The simulation requires questions q1, q2, and q3")

    reports = {}

    # Each simulated student gets a fresh, isolated progress file.
    with tempfile.TemporaryDirectory(prefix="studybridge_sim_") as temp_root:
        for profile_name, profile in profiles.items():
            student_dir = f"{temp_root}/{profile_name}"
            learner = LearnerModel(data_dir=student_dir)

            initial = {
                topic: round(float(info["mastery"]), 2)
                for topic, info in learner.get_progress().items()
            }

            exposures = []
            session_reports = []

            for session_number in range(1, sessions + 1):
                exposures.extend(question_ids)

                session_answers = {
                    question_id: profile["answers"][question_id]
                    for question_id in question_ids
                    if question_id in profile["answers"]
                }
                results = engine.evaluate_quiz(session_answers)
                updated_topics = set()

                for item in results["feedback"]:
                    topic = item["topic"]

                    if topic not in updated_topics:
                        learner.update_mastery(topic, results)
                        updated_topics.add(topic)

                session_reports.append({
                    "session": session_number,
                    "score": results["score"],
                    "total": results["total"],
                    "percentage": results["percentage"],
                })

            final = {
                topic: round(float(info["mastery"]), 2)
                for topic, info in learner.get_progress().items()
            }

            all_topics = sorted(set(initial) | set(final))
            gains = {
                topic: round(final.get(topic, 0) - initial.get(topic, 0), 2)
                for topic in all_topics
            }

            weakest_topic = min(
                final,
                key=lambda topic: final[topic]
            ) if final else None

            unique_questions = len(set(exposures))
            repeated_exposures = len(exposures) - unique_questions
            repetition_rate = (
                round(repeated_exposures / len(exposures) * 100, 1)
                if exposures else 0.0
            )

            reports[profile_name] = {
                "description": profile["description"],
                "sessions": session_reports,
                "initial_mastery": initial,
                "final_mastery": final,
                "mastery_gain": gains,
                "weakest_topic": weakest_topic,
                "question_exposures": len(exposures),
                "unique_questions": unique_questions,
                "repeated_question_exposures": repeated_exposures,
                "repetition_rate_percentage": repetition_rate,
            }

    return {
        "experiment": "StudyBridge AI simulated personalization",
        "sessions_per_student": sessions,
        "question_count_per_session": len(question_ids),
        "profiles": reports,
        "limitations": [
            "These are deterministic simulations, not real student outcomes.",
            "The current quiz repeats the same fixed questions in every session.",
            "Mastery is an application estimate, not a validated measure of learning.",
            "A mastery gain or loss does not establish educational effectiveness.",
        ],
    }
