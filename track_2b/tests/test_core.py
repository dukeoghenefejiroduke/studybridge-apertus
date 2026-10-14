"""
Standard library unit tests for StudyBridge AI core modules.
Runs offline without requiring external pip packages.
"""

import unittest
import os
import shutil
from app.ingestion import IngestionManager
from app.retrieval import RetrievalEngine
from app.tutor import TutorEngine
from app.assessment import AssessmentEngine
from app.learner_model import LearnerModel
from app.evaluation import EvaluationEngine

class TestStudyBridgeCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_processed_core"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.ingestion = IngestionManager(data_dir=self.test_dir)
        self.retrieval = RetrievalEngine(self.ingestion)
        self.tutor = TutorEngine(self.retrieval)
        self.assessment = AssessmentEngine()
        self.learner = LearnerModel(data_dir=self.test_dir)
        self.evaluation = EvaluationEngine(self.retrieval, self.tutor)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_ingestion(self):
        doc = self.ingestion.add_document("Test Doc", "notes", "Page 1", "00:01:00", "Neural networks process features.")
        self.assertEqual(doc["title"], "Test Doc")
        docs = self.ingestion.get_all_documents()
        self.assertTrue(len(docs) >= 4)
        self.assertEqual(docs[0]["title"], "Test Doc")

    def test_retrieval(self):
        results = self.retrieval.search("multimodal ai")
        self.assertTrue(len(results) > 0)

    def test_tutor(self):
        # 1. Supported question about cross-attention
        resp_ca = self.tutor.answer_question("cross-attention mechanisms")
        self.assertTrue(resp_ca["supported"])
        self.assertTrue(len(resp_ca["citations"]) > 0)

        # 2. Supported question about learner modelling
        resp_lm = self.tutor.answer_question("Bayesian Knowledge Tracing learner modeling")
        self.assertTrue(resp_lm["supported"])
        self.assertTrue(len(resp_lm["citations"]) > 0)

        # 3. Unsupported question about the capital of France
        resp_france = self.tutor.answer_question("What is the capital of France?")
        self.assertFalse(resp_france["supported"])
        self.assertEqual(resp_france["citations"], [])

        # 4. Unrelated question using different wording
        resp_unrelated = self.tutor.answer_question("How do airplanes fly across the Atlantic Ocean?")
        self.assertFalse(resp_unrelated["supported"])

        # 5. Empty query
        resp_empty = self.tutor.answer_question("   ")
        self.assertFalse(resp_empty["supported"])
        self.assertEqual(resp_empty["citations"], [])

        # 6. Relevant keyword appearing in an otherwise irrelevant context
        resp_keyword = self.tutor.answer_question("feedback on my chocolate cake baking recipe")
        self.assertFalse(resp_keyword["supported"])

    def test_assessment(self):
        questions = self.assessment.get_questions()
        self.assertTrue(len(questions) > 0)

        answers = {"q1": "B", "q2": "B", "q3": "B"}
        results = self.assessment.evaluate_quiz(answers)
        self.assertEqual(results["score"], 3)

    def test_learner_model(self):
        progress = self.learner.get_progress()
        self.assertIn("Multimodal AI", progress)

        quiz_results = {
            "feedback": [
                {"topic": "Multimodal AI", "correct": True},
                {"topic": "Multimodal AI", "correct": True}
            ]
        }
        updated = self.learner.update_mastery("Multimodal AI", quiz_results)
        self.assertGreater(updated["mastery"], 0.0)

    def test_evaluation(self):
        eval_report = self.evaluation.run_evaluation()
        self.assertIn("accuracy_percentage", eval_report)
        self.assertGreaterEqual(eval_report["accuracy_percentage"], 0.0)

if __name__ == "__main__":
    unittest.main()
