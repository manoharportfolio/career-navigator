import os
import json
from dotenv import load_dotenv

# Vertex AI (Gemini) SDK
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel, GenerationConfig

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
MODEL = os.getenv("MODEL", "gemini-1.5-flash").strip('"').strip("'")

# Init Vertex AI
vertex_init(project=PROJECT_ID, location=LOCATION)

# Reusable model object
_model = GenerativeModel(MODEL)

def _safe_json(text, fallback):
    try:
        return json.loads(text)
    except Exception:
        return fallback

def generate_career_suggestions(interests, skills, education):
    """
    Returns a list of 3 careers:
      [{ "name": "...", "demand": "High/Medium/Emerging", "desc": "..." }, ...]
    """
    prompt = f"""
You are a helpful career advisor for Indian students.

Student profile:
- Interests: {interests}
- Skills: {skills or "None provided"}
- Education Level: {education}

Task:
Suggest exactly 3 suitable career paths in India.
For EACH career, return:
- name (short)
- demand (High, Medium, or Emerging)
- desc (1 concise sentence in simple language)

Output ONLY valid JSON array. Example:
[
  {{"name": "Data Analyst", "demand": "High", "desc": "..." }},
  ...
]
"""
    resp = _model.generate_content(
        [prompt],
        generation_config=GenerationConfig(
            temperature=0.4,
            max_output_tokens=600,
        )
    )
    fallback = [
        {"name": "Data Analyst", "demand": "High", "desc": "Analyze data to find insights and support decisions."},
        {"name": "Cloud Engineer", "demand": "Medium", "desc": "Build and manage apps and infrastructure on cloud."},
        {"name": "UX Designer", "demand": "Emerging", "desc": "Design simple, user-friendly app and website experiences."}
    ]
    text = (resp.text or "").strip()
    return _safe_json(text, fallback)


def generate_roadmap(career):
    """
    Returns a roadmap dict:
    {
      "short_term": "...",
      "mid_term": "...",
      "long_term": "...",
      "progress": 0-100,
      "badge": "..."
    }
    """
    prompt = f"""
Create a clear, practical career roadmap for the role: {career}.
Audience: Indian student; keep it simple and action-focused.

Split into:
- short_term (0–6 months): concrete skills/courses to start
- mid_term (6–18 months): projects/certifications/internships
- long_term (2–3 years): job roles and next growth steps
Also include:
- progress: an estimated readiness % for a beginner (0–100)
- badge: a short motivational badge with one emoji

Output ONLY a single JSON object with these keys:
{{
  "short_term": "...",
  "mid_term": "...",
  "long_term": "...",
  "progress": 55,
  "badge": "Skill Unlocked: Python Basics 🏅"
}}
"""
    resp = _model.generate_content(
        [prompt],
        generation_config=GenerationConfig(
            temperature=0.5,
            max_output_tokens=700,
        )
    )
    fallback = {
        "short_term": "Learn Python and SQL basics; practice with small datasets.",
        "mid_term": "Build 2 projects, take one certification, start applying for internships.",
        "long_term": "Land an entry-level role; keep improving with real-world projects.",
        "progress": 50,
        "badge": "Momentum Unlocked 🚀"
    }
    text = (resp.text or "").strip()
    data = _safe_json(text, fallback)

    # Normalize keys in case the model returns different casing
    return {
        "short_term": data.get("short_term", fallback["short_term"]),
        "mid_term": data.get("mid_term", fallback["mid_term"]),
        "long_term": data.get("long_term", fallback["long_term"]),
        "progress": int(data.get("progress", fallback["progress"])),
        "badge": data.get("badge", fallback["badge"]),
    }
