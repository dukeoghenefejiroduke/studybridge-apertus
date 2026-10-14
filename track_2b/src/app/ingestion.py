"""
Document ingestion module for StudyBridge AI.
Handles lecture notes, slides, and textbooks, preserving source locations
such as page numbers, slide numbers, and video timestamps, including file uploads (TXT, MD, PDF).
"""

import os
import json
import io
import uuid
from werkzeug.utils import secure_filename

class IngestionManager:
    def __init__(self, data_dir="data/processed"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.documents_file = os.path.join(data_dir, "documents.json")
        self.documents = self._load_documents()

    def _load_documents(self):
        if os.path.exists(self.documents_file):
            try:
                with open(self.documents_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return [
            {
                "id": "doc_1",
                "title": "Multimodal AI Foundations (Lecture 1)",
                "type": "slides",
                "source": "Lecture 1 Slides, Slide 12",
                "timestamp": "00:14:20",
                "content": "Multimodal AI combines text, vision, and audio embeddings into shared latent spaces. Cross-attention mechanisms allow models to align visual regions with descriptive tokens."
            },
            {
                "id": "doc_2",
                "title": "Adaptive Learning Systems Handbook",
                "type": "textbook",
                "source": "Textbook Chapter 3, Page 45",
                "timestamp": None,
                "content": "Learner modeling tracks mastery probability per topic using Bayesian Knowledge Tracing (BKT) or Item Response Theory (IRT). Evidence-based feedback highlights misconceptions immediately."
            },
            {
                "id": "doc_3",
                "title": "Retrieval-Augmented Generation & Grounding",
                "type": "notes",
                "source": "Study Notes, Page 4",
                "timestamp": "00:08:15",
                "content": "Grounding ensures generated answers rely exclusively on retrieved context chunks. Unsupported queries are explicitly flagged to prevent hallucinations."
            },
            {
                "id": "doc_4",
                "title": "Machine Learning Notes",
                "type": "notes",
                "source": "ML Course Notes, Page 1",
                "timestamp": None,
                "content": "Supervised learning algorithms require labeled training data for classification tasks and regression models. Unsupervised learning algorithms work with unlabeled data to discover hidden patterns, cluster data points, or perform dimensionality reduction."
            },
            {
                "id": "doc_5",
                "title": "Neural Networks and Backpropagation",
                "type": "textbook",
                "source": "Textbook Chapter 5, Page 112",
                "timestamp": None,
                "content": "Neural networks use backpropagation and gradient descent to update weights during training, minimizing loss across layers."
            },
            {
                "id": "doc_6",
                "title": "Bayesian Knowledge Tracing in Education",
                "type": "notes",
                "source": "Research Paper, Page 2",
                "timestamp": None,
                "content": "Bayesian Knowledge Tracing (BKT) models student knowledge states as binary latent variables updated through practice observations."
            },
            {
                "id": "doc_7",
                "title": "Item Response Theory and Student Ability",
                "type": "slides",
                "source": "Slides Ch 4, Slide 8",
                "timestamp": "00:22:10",
                "content": "Item Response Theory (IRT) evaluates probability of correct response based on question difficulty and student ability parameters."
            },
            {
                "id": "doc_8",
                "title": "Vector Embeddings and Semantic Search",
                "type": "notes",
                "source": "Study Guide, Page 9",
                "timestamp": None,
                "content": "Vector embeddings represent text semantics in multi-dimensional space, enabling cosine similarity searches for retrieval."
            },
            {
                "id": "doc_9",
                "title": "Cross-Attention Mechanisms in Vision-Language Models",
                "type": "textbook",
                "source": "Textbook Chapter 2, Page 33",
                "timestamp": None,
                "content": "Cross-attention mechanisms allow models to query visual feature maps using textual token representations."
            },
            {
                "id": "doc_10",
                "title": "Hallucination Mitigation in RAG Systems",
                "type": "notes",
                "source": "Lecture Notes, Page 7",
                "timestamp": "00:11:00",
                "content": "Retrieval-augmented generation mitigates model hallucinations by supplying verifiable context and enforcing strict citation rules."
            },
            {
                "id": "doc_11",
                "title": "Evaluation Metrics for Intelligent Tutoring Systems",
                "type": "textbook",
                "source": "Textbook Chapter 8, Page 201",
                "timestamp": None,
                "content": "Evaluation metrics measure retrieval precision, citation accuracy, and pedagogical effectiveness of tutoring responses."
            },
            {
                "id": "doc_12",
                "title": "Natural Language Processing Tokenization and Stemming",
                "type": "notes",
                "source": "NLP Guide, Page 3",
                "timestamp": None,
                "content": "Tokenization breaks text into sub-words or words while stemming normalizes word variants for lexical analysis."
            },
            {
                "id": "doc_13",
                "title": "Reinforcement Learning from Human Feedback (RLHF)",
                "type": "slides",
                "source": "Advanced AI, Slide 15",
                "timestamp": "00:45:30",
                "content": "Reinforcement learning from human feedback aligns model outputs with user preferences using reward models and policy optimization."
            },
            {
                "id": "doc_14",
                "title": "Data Privacy and Secure Deployment in Sovereign Clouds",
                "type": "notes",
                "source": "Security Brief, Page 5",
                "timestamp": None,
                "content": "Sovereign cloud deployments ensure data residency, strict access controls, and encryption of sensitive records."
            },
            {
                "id": "doc_15",
                "title": "Automated Quiz Generation and Adaptive Difficulty Scaling",
                "type": "textbook",
                "source": "Textbook Chapter 6, Page 88",
                "timestamp": None,
                "content": "Automated quiz generation creates formative assessments from ingested documents, adjusting difficulty based on learner mastery."
            }
        ]

    def save_documents(self):
        with open(self.documents_file, "w") as f:
            json.dump(self.documents, f, indent=2)

    def add_document(self, title, doc_type, source, timestamp, content):
        doc_id = f"doc_{len(self.documents) + 1}_{uuid.uuid4().hex[:6]}"
        new_doc = {
            "id": doc_id,
            "title": title,
            "type": doc_type,
            "source": source,
            "timestamp": timestamp,
            "content": content
        }
        self.documents.insert(0, new_doc)
        self.save_documents()
        return new_doc

    def get_all_documents(self):
        return self.documents

    def process_file_upload(self, file_storage, title=None, doc_type="notes", source=None, timestamp=None):
        if not file_storage or not file_storage.filename:
            return {"success": False, "error": "No file provided"}, 400

        raw_filename = file_storage.filename
        filename = secure_filename(raw_filename) or os.path.basename(raw_filename) or "file"
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".txt", ".md", ".pdf", ".pptx"]:
            return {"success": False, "error": "Unsupported file format. Please upload .txt, .md, .pdf, or .pptx files."}, 400

        file_bytes = file_storage.read()
        if not file_bytes:
            return {"success": False, "error": "Uploaded file is empty."}, 400

        # Size limit: 5 MB
        max_size = 5 * 1024 * 1024
        if len(file_bytes) > max_size:
            return {"success": False, "error": "File exceeds maximum size limit of 5 MB."}, 413

        doc_title = title if title and title.strip() else os.path.splitext(filename)[0]

        if ext in [".txt", ".md"]:
            try:
                content = file_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                return {"success": False, "error": f"Failed to decode text file: {str(e)}"}, 400

            doc_source = source if source and source.strip() else f"File: {filename}"
            new_doc = self.add_document(
                title=doc_title,
                doc_type=doc_type,
                source=doc_source,
                timestamp=timestamp,
                content=content
            )
            return {"success": True, "document": new_doc}, 200

        elif ext == ".pdf":
            try:
                import pypdf
            except ImportError:
                return {"success": False, "error": "pypdf library is not installed. PDF processing is unavailable."}, 500

            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            except Exception as e:
                return {"success": False, "error": f"Failed to parse PDF file: {str(e)}"}, 400

            if not reader.pages:
                return {"success": False, "error": "PDF contains no pages."}, 400

            added_docs = []
            total_text_length = 0

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                total_text_length += len(page_text.strip())
                if page_text.strip():
                    page_source = source if source and source.strip() else f"Page {page_num}"
                    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
                    page_doc = {
                        "id": doc_id,
                        "title": f"{doc_title} (Page {page_num})",
                        "type": doc_type,
                        "source": page_source,
                        "timestamp": timestamp,
                        "content": page_text.strip()
                    }
                    added_docs.append(page_doc)

            if total_text_length == 0:
                return {"success": False, "error": "PDF contains no extractable text (it may be a scanned PDF or contain only images/diagrams, which are not supported for automated extraction)."}, 400

            for page_doc in reversed(added_docs):
                self.documents.insert(0, page_doc)

            self.save_documents()
            return {"success": True, "documents": added_docs, "count": len(added_docs)}, 200

        elif ext == ".pptx":
            try:
                import zipfile
                import xml.etree.ElementTree as ET
            except Exception as e:
                return {"success": False, "error": f"Failed to import xml/zip modules: {str(e)}"}, 500

            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    slide_files = sorted([f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")])
                    if not slide_files:
                        return {"success": False, "error": "PPTX contains no slide XML files."}, 400

                    added_docs = []
                    total_text_length = 0

                    for idx, slide_file in enumerate(slide_files, start=1):
                        xml_content = z.read(slide_file)
                        root = ET.fromstring(xml_content)
                        texts = []
                        for elem in root.iter():
                            if elem.tag.endswith('t') and elem.text:
                                texts.append(elem.text)
                        slide_text = " ".join(texts).strip()
                        total_text_length += len(slide_text)

                        if slide_text:
                            slide_source = source if source and source.strip() else f"Slide {idx}"
                            doc_id = f"doc_{uuid.uuid4().hex[:10]}"
                            slide_doc = {
                                "id": doc_id,
                                "title": f"{doc_title} (Slide {idx})",
                                "type": "slides",
                                "source": slide_source,
                                "timestamp": timestamp,
                                "content": slide_text
                            }
                            added_docs.append(slide_doc)

                    if total_text_length == 0:
                        return {"success": False, "error": "PPTX contains no extractable text."}, 400

                    for slide_doc in reversed(added_docs):
                        self.documents.insert(0, slide_doc)

                    self.save_documents()
                    return {"success": True, "documents": added_docs, "count": len(added_docs)}, 200
            except Exception as e:
                return {"success": False, "error": f"Failed to parse PPTX file: {str(e)}"}, 400

        return {"success": False, "error": "Unsupported file format."}, 400
