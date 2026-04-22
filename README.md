# 🎯 ResumeAI Screener

> AI-powered resume analysis with ATS scoring, skill gap detection, RAG-based job matching, and an interactive career coach — all running locally via Ollama.

---

## ✨ Features

| Tab | What it does |
|-----|-------------|
| **📄 Screen Resume** | Upload a PDF or paste text, match it against a job description, get an ATS score, skill breakdown, AI feedback, and a one-click resume rewrite |
| **🗄️ Job Bank (RAG)** | Build a local library of job descriptions; TF-IDF cosine similarity surfaces the most relevant ones for every analysis — no external vector DB required |
| **💬 Career Coach** | Multi-turn AI chatbot for interview prep, career transitions, salary negotiation, and skill planning |

### Highlights

- **ATS Match Score (0–100)** — weighted blend of skill overlap (60%) and keyword TF-IDF overlap (40%), displayed as a color-coded ring
- **Skill gap detection** — vocabulary of 100+ tech skills across languages, ML/AI, data, cloud, MLOps, backend, and frontend
- **AI analysis** — structured JSON output from Ollama: actionable feedback, top skills to learn, and project ideas to close the gap
- **Resume rewriter** — sends your resume + JD to the LLM and returns an optimized version you can download
- **RAG job bank** — seed with 10 built-in sample JDs (Google, OpenAI, Microsoft, Razorpay, etc.) or add your own; persisted to `data/job_bank.json`
- **100% local** — no API keys, no cloud calls; your resume data never leaves your machine

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Streamlit UI  (app.py)                  │
├──────────────────┬──────────────────┬─────────────────────┤
│  resume_parser   │     matcher      │     rag_engine       │
│  PDF / TXT  →   │  ATS score  +    │  Job bank  +        │
│  plain text      │  skill gap NLP   │  TF-IDF retrieval   │
├──────────────────┴──────────────────┴─────────────────────┤
│                   ai_engine  (ai_engine.py)                │
│            Ollama  /api/chat  →  local LLM                 │
└───────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com) installed and running

### 1. Start Ollama and pull a model

```bash
ollama serve
ollama pull llama3          # recommended
# alternatives: mistral, phi3, gemma2, llama3.2
```

### 2. Clone and install dependencies

```bash
git clone https://github.com/your-username/resume-screener.git
cd resume-screener
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📂 Project Structure

```
resume-screener/
├── app.py              # Streamlit UI — tabs, layout, session state
├── ai_engine.py        # Ollama API wrapper (analyze, rewrite, chat)
├── rag_engine.py       # TF-IDF RAG — job bank CRUD + similarity search
├── matcher.py          # ATS score computation + skill extraction
├── resume_parser.py    # PDF (PyPDF2 / pypdf) and TXT extraction
├── sample_jobs.py      # 10 pre-built job descriptions for seeding
├── requirements.txt
├── README.md
└── data/
    └── job_bank.json   # Auto-created; stores saved job descriptions
```

---

## ⚙️ Configuration

All settings live in the **sidebar** at runtime — no config files needed.

| Setting | Default | Description |
|---------|---------|-------------|
| Ollama URL | `http://localhost:11434` | Change if running Ollama on a remote host or non-default port |
| Model | Auto-detected from running Ollama instance | Any model you've pulled works; `llama3` gives the best balance of speed and quality |

---

## 🧠 How the RAG Works

1. **Index** — job descriptions are stored as raw text in `data/job_bank.json` (no embeddings database required)
2. **Retrieve** — at query time, TF-IDF vectors are computed for the input JD and all stored jobs; cosine similarity ranks them
3. **Augment** — the top-K most similar jobs are surfaced in the UI alongside the AI analysis

Because similarity is computed on-the-fly in pure Python, there are no external services to configure. The trade-off is that retrieval over very large banks (1,000+ JDs) will be slower; see the upgrade path below.

---

## 📦 Requirements

```
streamlit>=1.32.0
pandas>=2.0.0
requests>=2.31.0
pypdf>=3.0.0
PyPDF2>=3.0.0
```

---

## 💡 Upgrade Ideas

- **Semantic RAG** — swap TF-IDF for [Chroma](https://www.trychroma.com/) + `sentence-transformers` for embedding-based retrieval
- **Job scraping** — pull live listings from LinkedIn or Naukri using BeautifulSoup or Playwright
- **Score history** — persist every analysis run to SQLite for tracking improvement over time
- **Resume export** — generate a formatted `.docx` with `python-docx`
- **Cloud deployment** — host on Hugging Face Spaces or Railway with a remote Ollama endpoint
- **Auth layer** — add user accounts with Streamlit-Authenticator for multi-user use

---

## OUTPUT

 - ** <img width="1365" height="631" alt="image" src="https://github.com/user-attachments/assets/2db187c9-3a72-4299-a7a9-8fca6400501b" />
 - ** <img width="1365" height="642" alt="image" src="https://github.com/user-attachments/assets/1966fec0-320f-44fb-9029-8c437ebf71a5" />
 - ** <img width="1365" height="610" alt="image" src="https://github.com/user-attachments/assets/3cc312e9-02d5-4988-bf3e-38d9636c5671" />
 - ** <img width="1137" height="618" alt="image" src="https://github.com/user-attachments/assets/d60b351e-7c69-47eb-8d2b-c7f4f1028641" />


## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

