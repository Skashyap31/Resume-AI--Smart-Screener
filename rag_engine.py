import json
import os
import math
import re
from collections import Counter


JOBS_FILE = "data/job_bank.json"


def _tokenize(text: str) -> list:
    return re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b', text.lower())


def _tfidf_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity using simple TF-IDF."""
    tokens1 = _tokenize(text1)
    tokens2 = _tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    vocab = set(tokens1) | set(tokens2)

    def tf(tokens):
        c = Counter(tokens)
        return {t: c[t] / len(tokens) for t in c}

    tf1, tf2 = tf(tokens1), tf(tokens2)

    # IDF over two "documents"
    def vec(tf_map):
        return {t: tf_map.get(t, 0) * (1 + math.log(2 / (1 + (1 if t in tf1 else 0) + (1 if t in tf2 else 0))))
                for t in vocab}

    v1, v2 = vec(tf1), vec(tf2)
    dot = sum(v1[t] * v2[t] for t in vocab)
    mag1 = math.sqrt(sum(x**2 for x in v1.values()))
    mag2 = math.sqrt(sum(x**2 for x in v2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


class RAGEngine:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._jobs = self._load()

    def _load(self) -> list:
        if os.path.exists(JOBS_FILE):
            try:
                with open(JOBS_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save(self):
        with open(JOBS_FILE, "w") as f:
            json.dump(self._jobs, f, indent=2)

    def add_job(self, title: str, description: str):
        self._jobs.append({"title": title, "description": description})
        self._save()

    def count(self) -> int:
        return len(self._jobs)

    def get_all(self) -> list:
        return self._jobs

    def delete(self, index: int):
        if 0 <= index < len(self._jobs):
            self._jobs.pop(index)
            self._save()

    def clear(self):
        self._jobs = []
        self._save()

    def find_similar(self, query: str, top_k: int = 3) -> list:
        if not self._jobs:
            return []

        scored = []
        for job in self._jobs:
            sim = _tfidf_similarity(query, job["description"])
            scored.append({**job, "similarity": sim})

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]
