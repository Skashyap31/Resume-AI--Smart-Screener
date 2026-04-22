import requests
import json
import re


class AIEngine:
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _chat(self, system: str, messages: list, temperature: float = 0.7) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=90)
            if r.status_code == 200:
                return r.json().get("message", {}).get("content", "")
            return f"⚠️ Ollama error {r.status_code}"
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Run: `ollama serve`"
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out. Model may be loading — try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def analyze_resume(self, resume: str, jd: str, score: int, missing_skills: list) -> dict:
        missing_str = ", ".join(missing_skills) if missing_skills else "none"
        system = """You are an expert ATS resume analyst and career coach. 
Analyze the provided resume against the job description and return a JSON object.
Return ONLY valid JSON, no markdown fences, no extra text."""

        prompt = f"""Resume:
{resume[:3000]}

Job Description:
{jd[:2000]}

ATS Match Score: {score}/100
Missing Skills: {missing_str}

Return this exact JSON structure:
{{
  "feedback": "3-4 sentence professional feedback on the resume vs JD. Be specific. Mention actual missing skills.",
  "skills_to_learn": ["skill 1 with 1-line reason", "skill 2 with reason", "skill 3 with reason"],
  "projects": ["project idea 1 that demonstrates missing skills", "project idea 2", "project idea 3"]
}}"""

        raw = self._chat(system, [{"role": "user", "content": prompt}], temperature=0.5)
        
        try:
            # Strip any accidental markdown fences
            clean = re.sub(r"```(?:json)?|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "feedback": raw[:1000] if raw else "Could not generate analysis.",
                "skills_to_learn": [],
                "projects": []
            }

    def rewrite_resume(self, resume: str, jd: str) -> str:
        system = """You are a professional resume writer. Rewrite the resume to better match 
the job description. Keep it honest and professional. Use action verbs and quantify achievements."""
        
        prompt = f"""Original Resume:
{resume[:3000]}

Target Job Description:
{jd[:1500]}

Rewrite the resume to better match this job. Improve phrasing, highlight relevant experience, 
add relevant keywords from the JD, and suggest bullet points for missing areas."""

        return self._chat(system, [{"role": "user", "content": prompt}], temperature=0.6)

    def career_chat(self, user_message: str, history: list) -> str:
        system = """You are a world-class career coach with expertise in tech hiring, resume writing, 
interview preparation, and career growth. Give specific, actionable advice. Be concise (3-5 sentences 
unless detail is needed). Use bullet points for lists. Be encouraging but honest."""

        messages = [{"role": m["role"], "content": m["content"]} for m in history[-8:]]
        messages.append({"role": "user", "content": user_message})
        
        return self._chat(system, messages, temperature=0.75)
