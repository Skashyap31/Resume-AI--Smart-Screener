import re
from collections import Counter


# ── Master tech skill vocabulary ─────────────────────────────
TECH_SKILLS = [
    # Languages
    "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#",
    "ruby", "scala", "kotlin", "swift", "php", "r", "matlab", "bash", "perl",
    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "llm", "rag", "generative ai",
    "transformers", "bert", "gpt", "langchain", "llamaindex", "hugging face",
    "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost", "lightgbm",
    "opencv", "spacy", "nltk",
    # Data
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "pandas", "numpy", "spark", "hadoop", "hive", "kafka", "airflow",
    "dbt", "data pipeline", "etl", "data warehouse", "snowflake", "bigquery",
    # Cloud / MLOps
    "aws", "azure", "gcp", "docker", "kubernetes", "mlflow", "kubeflow",
    "ci/cd", "terraform", "github actions", "jenkins", "prometheus", "grafana",
    # APIs / Backend
    "fastapi", "flask", "django", "rest api", "graphql", "microservices",
    "grpc", "celery", "rabbitmq",
    # Frontend / Full-stack
    "react", "vue", "angular", "node.js", "next.js", "html", "css",
    # Tools / Practices
    "git", "agile", "scrum", "jira", "linux", "unit testing", "tdd",
    "a/b testing", "feature engineering", "model deployment", "vector database",
    "embedding", "fine-tuning", "prompt engineering", "streamlit",
]


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower().strip())


def extract_skills(text: str) -> set:
    text_lower = _normalize(text)
    found = set()
    for skill in TECH_SKILLS:
        # Use word boundaries for single-word skills, substring match for multi-word
        if ' ' in skill:
            if skill in text_lower:
                found.add(skill)
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)
    return found


def compute_match_score(resume_text: str, jd_text: str):
    """
    Returns (score: int 0-100, present_skills: list, missing_skills: list)
    Score = weighted combination of:
      - Skill overlap (60%)
      - Keyword TF overlap (40%)
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # ── Skill component
    if jd_skills:
        present = resume_skills & jd_skills
        missing = jd_skills - resume_skills
        skill_score = len(present) / len(jd_skills)
    else:
        present = resume_skills
        missing = set()
        skill_score = 0.5  # neutral if no known skills in JD

    # ── Keyword overlap component (general terms)
    def bag(text):
        stopwords = {"the","a","an","and","or","is","in","of","to","for","with",
                     "that","this","are","be","will","we","you","our","as","at",
                     "on","by","have","has","from","it","its","their","they",
                     "your","my","we're","i","he","she","do","does","not","if"}
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
        return Counter(w for w in words if w not in stopwords and len(w) > 2)

    r_bag = bag(resume_text)
    j_bag = bag(jd_text)

    jd_top_words = set(w for w, _ in j_bag.most_common(50))
    resume_words = set(r_bag.keys())
    kw_overlap = len(jd_top_words & resume_words) / max(len(jd_top_words), 1)

    # ── Combined score
    raw = 0.6 * skill_score + 0.4 * kw_overlap
    score = max(5, min(98, int(raw * 100)))

    return score, sorted(present), sorted(missing)
