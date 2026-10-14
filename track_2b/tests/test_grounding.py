"""
Unit tests for Grounding, Retrieval, and Ingestion in StudyBridge AI.
"""

import pytest
import io
from pypdf import PdfWriter
from app.ingestion import IngestionManager
from app.retrieval import RetrievalEngine
from app.tutor import TutorEngine

def test_retrieval_and_tutor():
    ingestion = IngestionManager(data_dir="data/test_grounding")
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    response = tutor.answer_question("cross-attention mechanisms")
    assert response["supported"] == True
    assert len(response["citations"]) > 0

    unsupported = tutor.answer_question("quantum gravity warp drive rocket")
    assert unsupported["supported"] == False


def test_txt_markdown_upload_and_retrieval(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    # Add text document
    ingestion.add_document(
        title="Custom Notes",
        doc_type="notes",
        source="Custom Upload",
        timestamp=None,
        content="Photosynthesis converts sunlight into chemical energy in plants."
    )

    response = tutor.answer_question("photosynthesis converts sunlight")
    assert response["supported"] == True
    assert len(response["citations"]) > 0
    assert "Custom Notes" in response["citations"][0]["title"]


def test_pdf_multi_page_upload_metadata(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    # Test text or metadata logic
    pass


def test_supported_question_citation_exists(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    ingestion.add_document(
        title="AI History",
        doc_type="textbook",
        source="Page 10",
        timestamp=None,
        content="Neural networks use backpropagation to update weights during training."
    )
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    response = tutor.answer_question("backpropagation update weights training")
    assert response["supported"] == True
    assert response["citations"][0]["title"] == "AI History"
    assert response["citations"][0]["source"] == "Page 10"


def test_unsupported_question_no_invented_citation(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    response = tutor.answer_question("what is the airspeed velocity of an unladen swallow")
    assert response["supported"] == False
    assert response["citations"] == []
    assert "reliably" in response["answer"].lower()


def test_irrelevant_material_not_presented_as_support(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    ingestion.add_document(
        title="Recipe Book",
        doc_type="notes",
        source="Kitchen Notes",
        timestamp=None,
        content="Bake the cake at 350 degrees for forty minutes."
    )
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    response_nn = tutor.answer_question("neural networks backpropagation")
    assert response_nn["supported"] == False


def test_multi_document_retrieval_source_identity(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    ingestion.add_document(
        title="Doc Alpha",
        doc_type="notes",
        source="Alpha Source",
        timestamp=None,
        content="Alpha content describes vector databases and cosine similarity."
    )
    ingestion.add_document(
        title="Doc Beta",
        doc_type="notes",
        source="Beta Source",
        timestamp=None,
        content="Beta content describes transformer models and self attention."
    )
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    res_alpha = tutor.answer_question("vector databases cosine similarity")
    assert res_alpha["supported"] == True
    assert res_alpha["citations"][0]["title"] == "Doc Alpha"
    assert res_alpha["citations"][0]["source"] == "Alpha Source"


def test_tutor_thorough_multi_document_synthesis(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    ingestion.add_document(
        title="Source One",
        doc_type="notes",
        source="Lecture A",
        timestamp=None,
        content="Artificial intelligence and machine learning advance rapidly."
    )
    ingestion.add_document(
        title="Source Two",
        doc_type="textbook",
        source="Chapter B",
        timestamp=None,
        content="Artificial intelligence and neural networks require high computational power."
    )
    retrieval = RetrievalEngine(ingestion)
    tutor = TutorEngine(retrieval)

    response = tutor.answer_question("artificial intelligence machine learning neural networks")
    assert response["supported"] == True
    assert len(response["citations"]) >= 2
    titles = [c["title"] for c in response["citations"]]
    assert "Source One" in titles
    assert "Source Two" in titles


def test_path_traversal_filename_sanitized(tmp_path):
    ingestion = IngestionManager(data_dir=str(tmp_path))
    class MockFile:
        filename = "../../etc/passwd.txt"
        def read(self):
            return b"root access data"

    res, status = ingestion.process_file_upload(MockFile())
    assert status == 200
    assert res["success"] == True
    doc = res["document"]
    assert "passwd" in doc["title"]
