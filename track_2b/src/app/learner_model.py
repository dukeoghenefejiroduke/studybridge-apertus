"""
Learner model module for StudyBridge AI.
Tracks per-topic learner mastery, confidence, and progress across sessions,
identifying weak topics for adaptive recommendations.
"""

import os
import json

class LearnerModel:
    def __init__(self, data_dir="data/processed"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.progress_file = os.path.join(data_dir, "learner_progress.json")
        self.progress = self._load_progress()

    def _load_progress(self):
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r") as f:
                    data = json.load(f)
                    for topic, info in data.items():
                        if "history" not in info:
                            info["history"] = [info.get("mastery", 0.5)]
                    return data
            except Exception:
                pass
        return {
            "Multimodal AI": {"mastery": 0.65, "sessions": 3, "status": "Developing", "history": [0.55, 0.60, 0.65]},
            "Learner Modeling": {"mastery": 0.80, "sessions": 4, "status": "Proficient", "history": [0.70, 0.75, 0.80]},
            "Grounding & RAG": {"mastery": 0.45, "sessions": 2, "status": "Needs Review", "history": [0.40, 0.45]}
        }

    def save_progress(self):
        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)

    def get_progress(self):
        return self.progress

    def update_mastery(self, topic, quiz_results):
        """
        Updates topic mastery based on quiz results and tracks historical progression.
        """
        if topic not in self.progress:
            self.progress[topic] = {"mastery": 0.50, "sessions": 1, "status": "Developing", "history": [0.50]}

        topic_items = [item for item in quiz_results.get("feedback", []) if item["topic"] == topic]
        if topic_items:
            correct_count = sum(1 for item in topic_items if item["correct"])
            topic_ratio = correct_count / len(topic_items)

            current_mastery = self.progress[topic]["mastery"]
            new_mastery = round(0.6 * current_mastery + 0.4 * topic_ratio, 2)
            new_mastery = max(0.0, min(1.0, new_mastery))

            self.progress[topic]["mastery"] = new_mastery
            self.progress[topic]["sessions"] += 1
            if "history" not in self.progress[topic]:
                self.progress[topic]["history"] = [current_mastery]
            self.progress[topic]["history"].append(new_mastery)
            # Keep history bounded
            self.progress[topic]["history"] = self.progress[topic]["history"][-10:]

            if new_mastery >= 0.75:
                self.progress[topic]["status"] = "Proficient"
            elif new_mastery >= 0.50:
                self.progress[topic]["status"] = "Developing"
            else:
                self.progress[topic]["status"] = "Needs Review"

            self.save_progress()
        return self.progress[topic]
