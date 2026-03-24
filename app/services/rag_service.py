"""Simple local RAG service.

This starter version uses TF-IDF over local runbook text files.
A production version would likely use embeddings plus a vector database.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import RUNBOOKS_DIR, DEFAULT_TOP_K
from app.seed_data import ensure_runbooks_exist


@dataclass
class RetrievedDoc:
    """Container for a retrieved runbook result."""

    filename: str
    content: str
    score: float


class LocalRAGService:
    """Loads local runbooks and returns the most relevant documents."""

    def __init__(self) -> None:
        ensure_runbooks_exist()

        # Read all runbook files into memory.
        self.paths: List[Path] = sorted(RUNBOOKS_DIR.glob("*.txt"))
        self.documents: List[str] = [path.read_text(encoding="utf-8") for path in self.paths]

        # Build a TF-IDF matrix once at startup.
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.documents) if self.documents else None

    def retrieve(self, *, site_id: str, asset_type: str, event_type: str, top_k: int = DEFAULT_TOP_K) -> List[RetrievedDoc]:
        """Return the most relevant local runbooks for the provided context."""
        if not self.documents or self.matrix is None:
            return []

        query = f"site {site_id} asset {asset_type} event {event_type}"
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()

        ranked_indices = scores.argsort()[::-1][:top_k]
        results: List[RetrievedDoc] = []

        for idx in ranked_indices:
            results.append(
                RetrievedDoc(
                    filename=self.paths[idx].name,
                    content=self.documents[idx],
                    score=float(scores[idx]),
                )
            )

        return results

    def build_action_list(self, *, site_id: str, asset_type: str, event_type: str) -> tuple[str, str]:
        """Create a simple operator action list from retrieved runbooks.

        Returns:
            recommended_actions: human-friendly action text
            supporting_docs: comma-separated supporting document names
        """
        docs = self.retrieve(site_id=site_id, asset_type=asset_type, event_type=event_type)

        if not docs:
            fallback = (
                "1. Validate the event source.\n"
                "2. Review recent site telemetry.\n"
                "3. Check whether this issue is already known.\n"
                "4. Escalate to site operations if the condition persists."
            )
            return fallback, "no_supporting_docs_found"

        actions = []
        supporting_docs = []

        for doc in docs:
            supporting_docs.append(doc.filename)

            # Keep only meaningful numbered lines from the runbook.
            for line in doc.content.splitlines():
                stripped = line.strip()
                if len(stripped) > 1 and stripped[0].isdigit() and "." in stripped:
                    actions.append(stripped)

        # Remove duplicates while preserving order.
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return "\n".join(unique_actions[:6]), ", ".join(supporting_docs)
