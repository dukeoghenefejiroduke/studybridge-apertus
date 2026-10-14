"""
Assessment engine for StudyBridge AI.

Provides a question bank, adaptive question selection, safe scoring,
and persistent question-exposure history.

Source references are explicitly marked as unlinked until questions
can be grounded in actual uploaded course materials.
"""

import json
import os
import uuid


class AssessmentEngine:
    def __init__(self, history_file="data/processed/assessment_history.json"):
        self.history_file = history_file

        self.questions = [
            {
                "id": "q1",
                "topic": "Multimodal AI",
                "type": "mcq",
                "difficulty": "medium",
                "prompt": "What role do cross-attention mechanisms play in Multimodal AI?",
                "options": [
                    "A) They compress video frames into audio streams.",
                    "B) They allow models to align visual regions with descriptive tokens.",
                    "C) They eliminate the need for training data.",
                    "D) They convert text directly to bytecode."
                ],
                "correct_answer": "B",
                "explanation": (
                    "Cross-attention allows information from one modality "
                    "to influence representations in another modality."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q2",
                "topic": "Learner Modeling",
                "type": "mcq",
                "difficulty": "medium",
                "prompt": "How is student mastery commonly estimated across sessions?",
                "options": [
                    "A) Random number generation",
                    "B) Bayesian Knowledge Tracing or other learner models",
                    "C) Disk storage size calculation",
                    "D) Network ping latency"
                ],
                "correct_answer": "B",
                "explanation": (
                    "Learner models estimate knowledge using evidence such "
                    "as assessment responses over time."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q3",
                "topic": "Grounding & RAG",
                "type": "mcq",
                "difficulty": "medium",
                "prompt": "Why is grounding important in educational retrieval-augmented generation?",
                "options": [
                    "A) It makes every answer longer.",
                    "B) It connects answers to retrieved evidence and helps reduce unsupported claims.",
                    "C) It removes the need for source documents.",
                    "D) It guarantees that every generated answer is correct."
                ],
                "correct_answer": "B",
                "explanation": (
                    "Grounding connects an answer to available evidence, "
                    "although retrieval alone cannot guarantee correctness."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q4",
                "topic": "Multimodal AI",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "Which example best describes multimodal learning?",
                "options": [
                    "A) Learning from text and images together",
                    "B) Sorting files only by their names",
                    "C) Counting characters in one text file",
                    "D) Compressing a folder without reading its contents"
                ],
                "correct_answer": "A",
                "explanation": (
                    "Multimodal learning combines information from two or "
                    "more modalities, such as text, images, audio, or video."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q5",
                "topic": "Multimodal AI",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "What is an embedding commonly used for?",
                "options": [
                    "A) Deleting source data",
                    "B) Turning every image into a video",
                    "C) Representing information as numerical vectors",
                    "D) Guaranteeing a model has no bias"
                ],
                "correct_answer": "C",
                "explanation": (
                    "An embedding represents information as a numerical "
                    "vector that can support comparison and retrieval."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q6",
                "topic": "Multimodal AI",
                "type": "mcq",
                "difficulty": "hard",
                "prompt": "Why might a multimodal model align text and image embeddings in a shared space?",
                "options": [
                    "A) To ensure all images have identical pixels",
                    "B) To remove the meaning of text",
                    "C) To avoid processing either modality",
                    "D) To make related text and images easier to compare"
                ],
                "correct_answer": "D",
                "explanation": (
                    "A shared representation space can place semantically "
                    "related text and images near one another."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q7",
                "topic": "Learner Modeling",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "What is the main purpose of tracking mastery by topic?",
                "options": [
                    "A) To identify areas where a learner may need more practice",
                    "B) To rank students by phone storage",
                    "C) To replace all teaching materials",
                    "D) To prevent learners from reviewing strong topics"
                ],
                "correct_answer": "A",
                "explanation": (
                    "Topic-level mastery estimates help identify learning "
                    "needs and guide study recommendations."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q8",
                "topic": "Learner Modeling",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "What should an adaptive tutor do after repeated incorrect answers on a topic?",
                "options": [
                    "A) Hide the topic permanently",
                    "B) Offer targeted review and appropriately chosen practice",
                    "C) Assume the learner has mastered it",
                    "D) Stop recording all progress"
                ],
                "correct_answer": "B",
                "explanation": (
                    "Repeated errors can indicate a need for targeted "
                    "explanation, review, and additional practice."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q9",
                "topic": "Learner Modeling",
                "type": "mcq",
                "difficulty": "hard",
                "prompt": "Why should mastery estimates not be treated as perfect measurements of knowledge?",
                "options": [
                    "A) Because assessment results contain no information",
                    "B) Because all students learn identically",
                    "C) Because a few answers may not represent the learner's full understanding",
                    "D) Because mastery can never change"
                ],
                "correct_answer": "C",
                "explanation": (
                    "A limited set of responses may be noisy or incomplete, "
                    "so mastery estimates should be treated as uncertain."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q10",
                "topic": "Grounding & RAG",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "What does a retriever do in a retrieval-augmented generation system?",
                "options": [
                    "A) Guarantees every answer is true",
                    "B) Deletes all irrelevant files permanently",
                    "C) Replaces every source with invented text",
                    "D) Finds potentially relevant information for a query"
                ],
                "correct_answer": "D",
                "explanation": (
                    "A retriever searches an indexed collection for material "
                    "that may help answer a query."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q11",
                "topic": "Grounding & RAG",
                "type": "mcq",
                "difficulty": "easy",
                "prompt": "What should a tutor do when the uploaded materials do not support an answer?",
                "options": [
                    "A) Acknowledge the limitation instead of inventing evidence",
                    "B) Invent a page number",
                    "C) Pretend it found a quotation",
                    "D) Always answer with complete certainty"
                ],
                "correct_answer": "A",
                "explanation": (
                    "A grounded tutor should distinguish available evidence "
                    "from information it cannot verify in the materials."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            },
            {
                "id": "q12",
                "topic": "Grounding & RAG",
                "type": "mcq",
                "difficulty": "hard",
                "prompt": "Why should a citation be checked against the retrieved passage?",
                "options": [
                    "A) Citations are only decorative",
                    "B) A citation label alone does not prove that the passage supports the claim",
                    "C) Every retrieved passage supports every question",
                    "D) Checking evidence makes retrieval unnecessary"
                ],
                "correct_answer": "B",
                "explanation": (
                    "The cited passage must actually support the associated "
                    "claim; the presence of a citation alone is insufficient."
                ),
                "source_reference": None,
                "source_status": "unlinked"
            }
        ]

    def generate_dynamic_question(self, doc):
        """Generate a practice MCQ from an ingested document."""
        content = doc.get("content", "").strip()
        if not content:
            return None

        sentences = [s.strip() for s in content.replace("!", ".").replace("?", ".").split(".") if len(s.strip()) > 20]
        if not sentences:
            return None

        sentence = sentences[0]
        topic = doc.get("type", "Multimodal AI").title()
        if topic not in ["Multimodal AI", "Learner Modeling", "Grounding & RAG"]:
            topic = "Multimodal AI"

        qid = f"dyn_{uuid.uuid4().hex[:8]}"
        q = {
            "id": qid,
            "topic": topic,
            "type": "mcq",
            "difficulty": "medium",
            "prompt": f"Based on '{doc.get('title', 'Study Material')}': Which statement best reflects the concept that '{sentence[:80]}...'?",
            "options": [
                f"A) {sentence}",
                "B) It represents unrelated noise or outdated data.",
                "C) It directly contradicts core curriculum.",
                "D) It requires no validation or citation."
            ],
            "correct_answer": "A",
            "explanation": f"Source document '{doc.get('title')}' establishes this exact concept.",
            "source_reference": f"{doc.get('title')} ({doc.get('source', 'Uploaded Material')})",
            "source_status": "linked"
        }
        self.questions.append(q)
        return q

    def _load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            seen = data.get("seen_question_ids", [])
            return seen if isinstance(seen, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def _public_question(self, question):
        """Remove the answer key and explanation from quiz questions."""
        return {
            key: value
            for key, value in question.items()
            if key not in ("correct_answer", "explanation")
        }

    def get_questions(self):
        """Return the full question bank without revealing answers."""
        return [
            self._public_question(question)
            for question in self.questions
        ]

    def select_questions(self, progress=None, limit=3, topic=None):
        """
        Select a small adaptive quiz.

        Selection first prefers unseen questions, spreads questions across
        topics, and then prioritizes topics with lower recorded mastery.
        Optional topic parameter allows scoping to specific topic(s).
        """
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("Question limit must be a positive integer.")

        valid_topics = {q["topic"] for q in self.questions}
        candidates = list(self.questions)

        if topic is not None:
            if isinstance(topic, str):
                requested_topics = [t.strip() for t in topic.split(",") if t.strip()]
            elif isinstance(topic, (list, tuple, set)):
                requested_topics = [str(t).strip() for t in topic if str(t).strip()]
            else:
                requested_topics = []

            if not requested_topics:
                raise ValueError("Topic scope cannot be empty.")

            for t in requested_topics:
                if t not in valid_topics:
                    raise ValueError(f"Unknown topic: '{t}'. Valid topics are {sorted(list(valid_topics))}")

            candidates = [q for q in candidates if q["topic"] in requested_topics]
            if not candidates:
                raise ValueError("No questions available for the requested topic scope.")

        progress = progress if isinstance(progress, dict) else {}
        history = self._load_history()
        seen = set(history)
        selected = []
        selected_topic_counts = {}

        for _ in range(min(limit, len(candidates))):
            def selection_key(question):
                t = question["topic"]
                topic_data = progress.get(t, {})
                try:
                    mastery = float(topic_data.get("mastery", 0.5))
                except (TypeError, ValueError, AttributeError):
                    mastery = 0.5

                mastery = max(0.0, min(1.0, mastery))
                is_seen = question["id"] in seen
                topic_count = selected_topic_counts.get(t, 0)

                # If all questions have been seen, prefer the least recently
                # encountered question rather than pretending it is unseen.
                last_seen = (
                    len(history) - 1 - history[::-1].index(question["id"])
                    if question["id"] in history
                    else -1
                )

                return (
                    is_seen,
                    topic_count,
                    mastery,
                    last_seen if is_seen else -1,
                    question["id"]
                )

            chosen = min(candidates, key=selection_key)
            candidates.remove(chosen)
            selected.append(self._public_question(chosen))
            selected_topic_counts[chosen["topic"]] = (
                selected_topic_counts.get(chosen["topic"], 0) + 1
            )

        return selected

    def record_questions_seen(self, question_ids):
        """Persist exposures for valid question IDs only."""
        valid_ids = {question["id"] for question in self.questions}
        history = self._load_history()

        if not isinstance(question_ids, (list, tuple, set)):
            return

        for question_id in question_ids:
            if question_id in valid_ids:
                history.append(question_id)

        # Keep a bounded history to prevent unlimited file growth.
        history = history[-200:]

        directory = os.path.dirname(self.history_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump({"seen_question_ids": history}, file, indent=2)

    def evaluate_quiz(self, user_answers):
        """
        Evaluate only the questions represented by submitted known IDs.

        An empty answer dictionary evaluates the full question bank so
        existing missing-answer checks remain meaningful.
        """
        if not isinstance(user_answers, dict):
            raise ValueError("Answers must be a dictionary.")

        question_map = {
            question["id"]: question
            for question in self.questions
        }

        if user_answers:
            submitted_questions = [
                question_map[qid]
                for qid in question_map
                if qid in user_answers
            ]
        else:
            submitted_questions = self.questions

        score = 0
        feedback = []

        for question in submitted_questions:
            qid = question["id"]
            raw_answer = user_answers.get(qid, "")

            if isinstance(raw_answer, str):
                user_answer = raw_answer.strip().upper()
                if len(user_answer) != 1 or user_answer not in "ABCD":
                    user_answer = ""
            else:
                user_answer = ""

            correct = user_answer == question["correct_answer"]

            if correct:
                score += 1

            feedback.append({
                "question_id": qid,
                "topic": question["topic"],
                "difficulty": question["difficulty"],
                "correct": correct,
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"],
                "source_reference": question["source_reference"],
                "source_status": question["source_status"]
            })

        total = len(submitted_questions)
        percentage = round((score / total) * 100, 1) if total else 0.0

        return {
            "score": score,
            "total": total,
            "percentage": percentage,
            "feedback": feedback
        }
