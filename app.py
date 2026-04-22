import streamlit as st
import json
import os
from rag_engine import RAGEngine
from ai_engine import AIEngine
from resume_parser import extract_resume_text
from matcher import compute_match_score

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeAI — Smart Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

.stApp { background: #0a0e1a; color: #e8eaf0; }

.score-ring {
    width: 140px; height: 140px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem; font-weight: 700;
    margin: 0 auto 1rem;
    border: 4px solid;
}
.score-high  { border-color: #00d4aa; color: #00d4aa; background: rgba(0,212,170,0.08); }
.score-mid   { border-color: #f59e0b; color: #f59e0b; background: rgba(245,158,11,0.08); }
.score-low   { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,0.08); }

.skill-tag {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; margin: 3px;
    font-family: 'JetBrains Mono', monospace;
}
.skill-present { background: rgba(0,212,170,0.15); color: #00d4aa; border: 1px solid rgba(0,212,170,0.3); }
.skill-missing { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

.card {
    background: #131929; border: 1px solid #1e2d45;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
}
.section-title {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.15em;
    color: #6b7fa3; text-transform: uppercase; margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")
    
    @st.cache_data(ttl=20)
    def get_models(url):
        import requests
        try:
            r = requests.get(f"{url}/api/tags", timeout=4)
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except: pass
        return []

    models = get_models(ollama_url)
    if models:
        model = st.selectbox("🤖 Model", models)
        st.success(f"✅ {len(models)} model(s) online")
    else:
        st.warning("⚠️ Ollama offline")
        model = st.text_input("Model name", value="llama3")
        st.code("ollama serve\nollama pull llama3", language="bash")

    st.markdown("---")
    st.markdown("### 📚 RAG Job Bank")
    rag = RAGEngine()
    st.caption(f"{rag.count()} job descriptions stored")
    
    if st.button("🗑️ Clear Job Bank"):
        rag.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Built with Ollama · RAG · NLP")

# ─── Header ───────────────────────────────────────────────────
st.markdown("# 🎯 ResumeAI Screener")
st.markdown("**AI-powered resume analysis with RAG-based job matching**")
st.markdown("---")

ai = AIEngine(model=model, base_url=ollama_url)

# ─── Tabs ─────────────────────────────────────────────────────
tab_screen, tab_rag, tab_chat = st.tabs(["📄 Screen Resume", "🗄️ Job Bank (RAG)", "💬 Career Coach"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — SCREEN RESUME
# ══════════════════════════════════════════════════════════════
with tab_screen:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📎 Upload Resume")
        resume_file = st.file_uploader("PDF or TXT", type=["pdf", "txt"])
        resume_text_input = st.text_area("Or paste resume text", height=200, placeholder="Paste your resume content here...")

        st.markdown("### 📋 Job Description")
        jd_text = st.text_area("Paste job description", height=200,
            placeholder="Paste the full job description you're applying for...")

        jd_title = st.text_input("Job Title (optional)", placeholder="e.g. Senior Data Scientist")

        # Save to RAG bank option
        save_to_rag = st.checkbox("📚 Save this JD to Job Bank (RAG)")
        
        analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

    with col_right:
        if analyze_btn:
            # Extract resume text
            resume_text = ""
            if resume_file:
                resume_text = extract_resume_text(resume_file)
            elif resume_text_input.strip():
                resume_text = resume_text_input.strip()

            if not resume_text:
                st.error("Please upload a resume or paste resume text.")
            elif not jd_text.strip():
                st.error("Please paste a job description.")
            else:
                # Save JD to RAG if requested
                if save_to_rag and jd_text.strip():
                    rag.add_job(jd_title or "Untitled Job", jd_text)
                    st.success("✅ Job saved to RAG bank")

                with st.spinner("🧠 Analyzing with AI..."):
                    # Compute match score
                    score, present_skills, missing_skills = compute_match_score(resume_text, jd_text)

                    # Get AI analysis
                    analysis = ai.analyze_resume(resume_text, jd_text, score, missing_skills)

                    # RAG — find similar jobs
                    similar_jobs = rag.find_similar(jd_text, top_k=3)

                # ── Score Display
                score_class = "score-high" if score >= 70 else ("score-mid" if score >= 45 else "score-low")
                score_emoji = "🟢" if score >= 70 else ("🟡" if score >= 45 else "🔴")
                
                st.markdown(f"""
                <div class="card" style="text-align:center">
                    <p class="section-title">ATS Match Score</p>
                    <div class="score-ring {score_class}">{score}</div>
                    <p style="color:#6b7fa3;font-size:0.9rem">{score_emoji} {'Strong Match' if score>=70 else 'Moderate Match' if score>=45 else 'Weak Match'}</p>
                </div>
                """, unsafe_allow_html=True)

                # ── Skills
                st.markdown(f"""<div class="card">
                    <p class="section-title">✅ Skills Present ({len(present_skills)})</p>
                    {"".join(f'<span class="skill-tag skill-present">{s}</span>' for s in present_skills) or '<em style="color:#6b7fa3">None detected</em>'}
                    <br><br>
                    <p class="section-title">❌ Missing Skills ({len(missing_skills)})</p>
                    {"".join(f'<span class="skill-tag skill-missing">{s}</span>' for s in missing_skills) or '<em style="color:#6b7fa3">None — great coverage!</em>'}
                </div>""", unsafe_allow_html=True)

                # ── AI Feedback
                st.markdown("### 🤖 AI Analysis")
                st.markdown(analysis.get("feedback", "No feedback generated."))

                # ── Skills to learn
                if analysis.get("skills_to_learn"):
                    st.markdown("### 📈 Skills to Learn")
                    for item in analysis["skills_to_learn"]:
                        st.markdown(f"- {item}")

                # ── Projects to build
                if analysis.get("projects"):
                    st.markdown("### 🛠️ Projects to Build")
                    for p in analysis["projects"]:
                        st.markdown(f"- {p}")

                # ── Rewrite Resume button
                st.markdown("---")
                if st.button("✨ Rewrite My Resume Section", use_container_width=True):
                    with st.spinner("Rewriting..."):
                        rewritten = ai.rewrite_resume(resume_text, jd_text)
                    st.markdown("### ✨ Improved Resume")
                    st.text_area("Copy this improved version:", rewritten, height=300)
                    st.download_button("⬇️ Download", rewritten, file_name="improved_resume.txt")

                # ── Similar Jobs from RAG
                if similar_jobs:
                    st.markdown("### 🔍 Similar Jobs (from RAG Bank)")
                    for job in similar_jobs:
                        with st.expander(f"📌 {job['title']} — {job['similarity']:.0%} similar"):
                            st.write(job["description"][:400] + "...")

# ══════════════════════════════════════════════════════════════
# TAB 2 — RAG JOB BANK
# ══════════════════════════════════════════════════════════════
with tab_rag:
    st.markdown("### 📚 Manage Your Job Description Bank")
    st.markdown("Store job descriptions for RAG-based retrieval. The more JDs you store, the smarter the matching gets.")

    col_add, col_view = st.columns([1, 1], gap="large")

    with col_add:
        st.markdown("#### ➕ Add Job Description")
        new_title = st.text_input("Job Title", key="rag_title")
        new_company = st.text_input("Company (optional)", key="rag_company")
        new_jd = st.text_area("Job Description", height=250, key="rag_jd")
        if st.button("💾 Save to Job Bank", use_container_width=True):
            if new_title and new_jd:
                rag.add_job(f"{new_title} @ {new_company}" if new_company else new_title, new_jd)
                st.success("✅ Saved!")
                st.rerun()
            else:
                st.error("Title and description required.")

        # Bulk seed with sample jobs
        if st.button("🌱 Seed with Sample Jobs (10 JDs)", use_container_width=True):
            from sample_jobs import SAMPLE_JOBS
            for title, desc in SAMPLE_JOBS:
                rag.add_job(title, desc)
            st.success(f"✅ Added {len(SAMPLE_JOBS)} sample job descriptions!")
            st.rerun()

    with col_view:
        st.markdown("#### 📋 Stored Job Descriptions")
        all_jobs = rag.get_all()
        if all_jobs:
            for i, job in enumerate(all_jobs):
                with st.expander(f"[{i+1}] {job['title']}"):
                    st.write(job["description"][:500] + ("..." if len(job["description"]) > 500 else ""))
                    if st.button(f"🗑️ Delete", key=f"del_{i}"):
                        rag.delete(i)
                        st.rerun()
        else:
            st.info("No jobs stored yet. Add some above or seed with sample jobs.")

# ══════════════════════════════════════════════════════════════
# TAB 3 — CAREER COACH CHATBOT
# ══════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("### 💬 Career Coach AI")
    st.markdown("Ask anything about resumes, interviews, career transitions, or skill building.")

    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = [
            {"role": "assistant", "content": "👋 Hi! I'm your Career Coach. Ask me anything — resume tips, interview prep, which skills to learn, or how to switch careers!"}
        ]

    for msg in st.session_state.coach_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    suggestions = ["How do I improve my LinkedIn?", "What skills are hot in 2025?", "How to negotiate salary?", "Tips for technical interviews?"]
    cols = st.columns(len(suggestions))
    for i, (c, s) in enumerate(zip(cols, suggestions)):
        with c:
            if st.button(s, key=f"coach_sugg_{i}", use_container_width=True):
                st.session_state["coach_pending"] = s

    pending = st.session_state.pop("coach_pending", None)
    user_input = st.chat_input("Ask your career question...") or pending

    if user_input:
        st.session_state.coach_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = ai.career_chat(user_input, st.session_state.coach_messages[:-1])
            st.markdown(reply)
        st.session_state.coach_messages.append({"role": "assistant", "content": reply})

    if len(st.session_state.coach_messages) > 1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.coach_messages = [st.session_state.coach_messages[0]]
            st.rerun()
