"""
Evaluation module for StudyBridge AI.

Reports a small tutoring benchmark and a deterministic personalization
simulation. Results are diagnostic software measurements, not proof of
real-world educational effectiveness.
"""

from app.personalization_evaluation import simulate_student_profiles


class EvaluationEngine:
    def __init__(self, retrieval_engine, tutor_engine):
        self.retrieval_engine = retrieval_engine
        self.tutor_engine = tutor_engine

    def run_evaluation(self):
        test_cases = [
            {
                "id": "tc_1",
                "query": "What do cross-attention mechanisms do?",
                "expected_keyword": "align visual regions",
            },
            {
                "id": "tc_2",
                "query": "How is student mastery tracked?",
                "expected_keyword": "Bayesian Knowledge Tracing",
            },
            {
                "id": "tc_3",
                "query": "Why is grounding important?",
                "expected_keyword": "prevent hallucinations",
            },
        ]

        results = []
        passed = 0

        for case in test_cases:
            response = self.tutor_engine.answer_question(case["query"])
            answer = response.get("answer", "")
            grounded = bool(response.get("supported", False))
            relevant = (
                case["expected_keyword"].lower() in answer.lower()
            )
            success = grounded and relevant

            if success:
                passed += 1

            results.append({
                "id": case["id"],
                "query": case["query"],
                "expected_keyword": case["expected_keyword"],
                "grounded": grounded,
                "relevant": relevant,
                "success": success,
                "answer": answer,
            })

        total = len(test_cases)
        accuracy = round(passed / total * 100, 1) if total else 0.0
        grounding_score = (
            round(sum(item["grounded"] for item in results) / total, 2)
            if total else 0.0
        )

        # Run simulated students with isolated temporary progress files.
        personalization = simulate_student_profiles(sessions=3)

        profiles = personalization["profiles"]
        priority_checks = {}

        for profile_name, profile in profiles.items():
            final_mastery = profile["final_mastery"]

            if final_mastery:
                weakest_topic = min(
                    final_mastery,
                    key=final_mastery.get,
                )
                priority_checks[profile_name] = {
                    "expected_high_priority_topic": weakest_topic,
                    "matches_simulated_weakest_topic": (
                        weakest_topic == profile["weakest_topic"]
                    ),
                }

        priority_check_count = len(priority_checks)
        priority_check_passes = sum(
            item["matches_simulated_weakest_topic"]
            for item in priority_checks.values()
        )

        return {
            "total_test_cases": total,
            "passed": passed,
            "accuracy_percentage": accuracy,
            "metrics": {
                "grounding_score": grounding_score,
            },
            "test_results": results,
            "personalization_evaluation": {
                **personalization,
                "weak_topic_consistency": {
                    "passed": priority_check_passes,
                    "total": priority_check_count,
                    "percentage": (
                        round(
                            priority_check_passes
                            / priority_check_count * 100,
                            1,
                        )
                        if priority_check_count else 0.0
                    ),
                    "checks": priority_checks,
                },
            },
        }
