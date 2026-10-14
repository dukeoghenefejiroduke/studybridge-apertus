"""
Unit tests for file uploads, PDF processing, API endpoints, and persistence in StudyBridge AI.
"""

import unittest
import os
import shutil
import io
from app.main import app
from app.ingestion import IngestionManager

class TestFileUploadAndAPI(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_upload_processed"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_flask_upload_txt(self):
        data = {
            "file": (io.BytesIO(b"Python is a high-level programming language used in AI."), "intro.txt"),
            "title": "Intro to Python",
            "type": "notes"
        }
        res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        res_json = res.get_json()
        self.assertTrue(res_json["success"])
        self.assertEqual(res_json["document"]["title"], "Intro to Python")

    def test_upload_markdown(self):
        data = {
            "file": (io.BytesIO(b"# Markdown Header\nSome markdown notes."), "guide.md"),
            "title": "Markdown Guide",
            "type": "textbook"
        }
        res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_reject_unsupported_extension(self):
        data = {
            "file": (io.BytesIO(b"executable binary content"), "malware.exe"),
            "title": "Bad File",
            "type": "notes"
        }
        res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_reject_empty_file(self):
        data = {
            "file": (io.BytesIO(b""), "empty.txt"),
            "title": "Empty File",
            "type": "notes"
        }
        res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_reject_oversized_file(self):
        large_content = b"A" * (6 * 1024 * 1024)
        data = {
            "file": (io.BytesIO(large_content), "large.txt"),
            "title": "Large File",
            "type": "notes"
        }
        res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 413)

    def test_pdf_no_text_handling(self):
        try:
            from pypdf import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=300, height=300)
            pdf_bytes_io = io.BytesIO()
            writer.write(pdf_bytes_io)
            pdf_bytes = pdf_bytes_io.getvalue()

            data = {
                "file": (io.BytesIO(pdf_bytes), "blank.pdf"),
                "title": "Blank PDF",
                "type": "textbook"
            }
            res = self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 400)
            self.assertIn("no extractable text", res.get_json()["error"].lower())
        except ImportError:
            pass

    def test_persistence_after_reload(self):
        ingestion = IngestionManager(data_dir=self.test_dir)
        ingestion.add_document("Persist Doc", "notes", "Source 1", None, "Persistence test content.")

        ingestion_reloaded = IngestionManager(data_dir=self.test_dir)
        docs = ingestion_reloaded.get_all_documents()
        found = any(d["title"] == "Persist Doc" for d in docs)
        self.assertTrue(found)

    def test_original_json_paste_api(self):
        payload = {
            "title": "JSON Paste Doc",
            "type": "notes",
            "source": "Pasted Notes",
            "content": "Quantum computing uses qubits for parallel processing."
        }
        res = self.client.post("/api/materials", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_tutor_retrieval_of_uploaded_content(self):
        data = {
            "file": (io.BytesIO(b"Supervised learning algorithms require labeled training data for classification tasks."), "ml_notes.txt"),
            "title": "Machine Learning Notes",
            "type": "notes"
        }
        self.client.post("/api/materials/upload", data=data, content_type="multipart/form-data")

        res = self.client.post("/api/tutor", json={"query": "supervised learning algorithms"})
        self.assertEqual(res.status_code, 200)
        ans = res.get_json()
        self.assertTrue(ans["supported"])
        self.assertIn("supervised learning", ans["answer"].lower())

if __name__ == "__main__":
    unittest.main()
