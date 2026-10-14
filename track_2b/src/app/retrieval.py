"""
Retrieval module for StudyBridge AI.

Searches ingested learning materials using normalized keyword matching
and returns relevant chunks with traceable source citations.
"""

import re


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "do", "does", "did", "what", "which", "who", "whom",
    "when", "where", "why", "how", "can", "could", "would", "should",
    "will", "may", "might", "must", "of", "in", "on", "at", "to",
    "for", "from", "by", "with", "and", "or", "but", "it", "its",
    "this", "that", "these", "those", "i", "we", "you", "they",
    "he", "she", "me", "my", "our", "your", "their", "as", "if",
    "about", "into", "through", "between", "during", "after", "before",
    "explain", "describe", "tell", "show", "give", "please",
    "important", "importance", "role", "purpose"
}


def normalize_word(word):
    """Apply lightweight normalization without external dependencies."""
    word = word.lower()

    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"

    if len(word) > 5 and word.endswith("ing"):
        word = word[:-3]
        if len(word) > 2 and word[-1] == word[-2]:
            word = word[:-1]
        return word

    if len(word) > 4 and word.endswith("ed"):
        word = word[:-2]
        if len(word) > 2 and word[-1] == word[-2]:
            word = word[:-1]
        return word

    if len(word) > 4 and word.endswith("es"):
        return word[:-2]

    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]

    return word


def tokenize(text):
    """Extract normalized words while excluding unhelpful query terms."""
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())

    return [
        normalize_word(word)
        for word in words
        if word not in STOPWORDS and len(word) > 1
    ]


class RetrievalEngine:
    def __init__(self, ingestion_manager):
        self.ingestion_manager = ingestion_manager

    def search(self, query, top_k=3):
        if not isinstance(query, str) or not query.strip():
            return []

        if not isinstance(top_k, int) or top_k < 1:
            return []

        documents = self.ingestion_manager.get_all_documents()

        if not documents:
            return []

        query_terms = tokenize(query)

        if not query_terms:
            return []

        # Unique terms prevent repeated words from inflating relevance.
        query_terms = set(query_terms)
        scored_results = []

        for doc in documents:
            content = doc.get("content", "")
            title = doc.get("title", "")

            content_terms = set(tokenize(content))
            title_terms = set(tokenize(title))

            # Title matches are useful, but actual content is stronger evidence.
            matched_content = query_terms & content_terms
            matched_title = query_terms & title_terms
            matched_terms = matched_content | matched_title

            if not matched_terms:
                continue

            coverage = len(matched_terms) / len(query_terms)

            # Require meaningful overlap for multi-term questions.
            if len(query_terms) == 1:
                relevant = coverage >= 1.0
            else:
                relevant = (
                    len(matched_terms) >= 2 and coverage >= 0.40
                ) or coverage >= 0.80

            if not relevant:
                continue

            # Small bonus for terms found in the actual passage.
            content_coverage = (
                len(matched_content) / len(query_terms)
            )

            score = min(
                1.0,
                coverage * 0.85 + content_coverage * 0.15
            )

            scored_results.append({
                "document_id": doc.get("id"),
                "title": title,
                "source": doc.get("source"),
                "timestamp": doc.get("timestamp"),
                "content": content,
                "score": round(score, 2)
            })

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_results[:top_k]