"""
Main Flask application for StudyBridge AI.
Provides dashboard, learning materials, tutor Q&A, practice quiz, and learning progress API endpoints.
"""

from flask import Flask, render_template, request, jsonify
from app.ingestion import IngestionManager
from app.retrieval import RetrievalEngine
from app.tutor import TutorEngine
from app.assessment import AssessmentEngine
from app.learner_model import LearnerModel
from app.evaluation import EvaluationEngine

app = Flask(__name__)

ingestion_manager = IngestionManager()
retrieval_engine = RetrievalEngine(ingestion_manager)
tutor_engine = TutorEngine(retrieval_engine)
assessment_engine = AssessmentEngine()
learner_model = LearnerModel()
evaluation_engine = EvaluationEngine(retrieval_engine, tutor_engine)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    docs = ingestion_manager.get_all_documents()
    progress = learner_model.get_progress()
    eval_report = evaluation_engine.run_evaluation()
    return jsonify({
        "status": "online",
        "project": "StudyBridge AI",
        "track": "Hack Apertus 2026 — Track 2B: Own Project",
        "document_count": len(docs),
        "progress": progress,
        "evaluation_summary": eval_report
    })

@app.route("/api/materials", methods=["GET", "POST"])
def api_materials():
    if request.method == "POST":
        data = request.json or {}
        title = data.get("title", "Untitled Document")
        doc_type = data.get("type", "notes")
        source = data.get("source", "User Upload")
        timestamp = data.get("timestamp")
        content = data.get("content", "")

        new_doc = ingestion_manager.add_document(title, doc_type, source, timestamp, content)
        assessment_engine.generate_dynamic_question(new_doc)
        return jsonify({"success": True, "document": new_doc})

    return jsonify({"documents": ingestion_manager.get_all_documents()})

@app.route("/api/materials/upload", methods=["POST"])
def api_materials_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file_storage = request.files["file"]
    title = request.form.get("title", "")
    doc_type = request.form.get("type", "notes")
    source = request.form.get("source", "")
    timestamp = request.form.get("timestamp", "")

    result, status_code = ingestion_manager.process_file_upload(
        file_storage, title=title, doc_type=doc_type, source=source, timestamp=timestamp
    )
    if status_code == 200:
        if "document" in result:
            assessment_engine.generate_dynamic_question(result["document"])
        elif "documents" in result:
            for doc in result["documents"][:3]:  # generate questions for up to 3 pages/slides
                assessment_engine.generate_dynamic_question(doc)
    return jsonify(result), status_code

@app.route("/api/tutor", methods=["POST"])
def api_tutor():
    data = request.get_json(silent=True) or {}

    # Accept both "query" and "question" for compatibility.
    query = data.get("query") or data.get("question") or ""

    response = tutor_engine.answer_question(query)
    return jsonify(response)

@app.route("/api/quiz/topics", methods=["GET"])
def api_quiz_topics():
    topics = sorted(list({q["topic"] for q in assessment_engine.questions}))
    return jsonify({"topics": topics})

@app.route("/api/quiz", methods=["GET"])
def api_quiz_get():
    topic_param = request.args.get("topic") or request.args.get("topics")
    try:
        questions = assessment_engine.select_questions(
            progress=learner_model.get_progress(),
            limit=3,
            topic=topic_param
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"questions": questions})

@app.route("/api/quiz/submit", methods=["POST"])
def api_quiz_submit():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object."
        }), 400

    answers = data.get("answers")

    if not isinstance(answers, dict):
        return jsonify({
            "error": "The 'answers' field must be an object mapping question IDs to answers."
        }), 400

    try:
        results = assessment_engine.evaluate_quiz(answers)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    # Record only valid question IDs that were included in this submission.
    assessment_engine.record_questions_seen(
        [item["question_id"] for item in results["feedback"]]
    )

    # Update each topic at most once per submission.
    updated_topics = set()

    for item in results["feedback"]:
        topic = item["topic"]

        if topic not in updated_topics:
            learner_model.update_mastery(topic, results)
            updated_topics.add(topic)

    return jsonify(results)


def build_study_recommendations(progress):
    """Recommend study actions using mastery scores and indexed materials."""
    recommendations = []

    topic_guidance = {
        "Multimodal AI": {
            "query": "multimodal AI vision audio text cross-attention embeddings",
            "action": "Review how text, images, and audio are aligned.",
            "practice": "Explain how cross-attention connects visual regions with descriptive tokens."
        },
        "Learner Modeling": {
            "query": "learner mastery Bayesian Knowledge Tracing adaptive learning",
            "action": "Review learner mastery estimation and adaptive feedback.",
            "practice": "Explain how a learner model can use assessment results to track mastery."
        },
        "Grounding & RAG": {
            "query": "grounding retrieval augmented generation hallucinations retrieved context",
            "action": "Review how retrieval and evidence reduce unsupported answers.",
            "practice": "Ask a question not covered by your materials and check whether the tutor declines to guess."
        }
    }

    for topic, info in sorted(
        progress.items(),
        key=lambda item: float(item[1].get("mastery", 0))
    ):
        try:
            mastery = max(0.0, min(1.0, float(info.get("mastery", 0))))
        except (TypeError, ValueError):
            mastery = 0.0

        guidance = topic_guidance.get(topic, {
            "query": topic,
            "action": "Review the key concepts for this topic.",
            "practice": "Summarize the topic in your own words, then test yourself."
        })

        if mastery < 0.50:
            priority = "High"
            reason = "This topic currently has the lowest mastery. Review it first."
        elif mastery < 0.75:
            priority = "Medium"
            reason = "More practice could help strengthen your understanding."
        else:
            priority = "Maintain"
            reason = "Your mastery is strong. Use practice to retain it."

        materials = retrieval_engine.search(guidance["query"], top_k=2)

        recommendations.append({
            "topic": topic,
            "mastery_percentage": round(mastery * 100),
            "priority": priority,
            "reason": reason,
            "action": guidance["action"],
            "practice": guidance["practice"],
            "materials": [
                {
                    "title": item.get("title", "Untitled material"),
                    "source": item.get("source", "Source not specified"),
                    "timestamp": item.get("timestamp"),
                    "relevance": item.get("score", 0)
                }
                for item in materials
            ]
        })

    return recommendations


@app.route("/api/progress", methods=["GET"])
def api_progress():
    progress = learner_model.get_progress()
    return jsonify({
        "progress": progress,
        "recommendations": build_study_recommendations(progress)
    })

@app.route("/api/evaluation", methods=["GET"])
def api_evaluation():
    return jsonify(evaluation_engine.run_evaluation())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
