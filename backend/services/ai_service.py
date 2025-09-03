import os
import json
import re
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
    """Try to parse JSON safely, fallback if invalid."""
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'(\{.*\}|\[.*\])', text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return fallback
        return fallback


def _call_model(prompt, temperature=0.6, max_tokens=1000):
    resp = _model.generate_content(
        [prompt],
        generation_config=GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    )
    return (resp.text or "").strip()


# ------------------ Generate roadmaps for ALL mentioned careers ------------------ #
def generate_all_roadmaps(interests, skills="", education=""):
    """
    Takes multiple careers from interests input (comma/semicolon separated).
    Returns a dict with roadmaps for EACH career, where each career has 3 paths:
      dream_path, skill_path, hybrid_path
    """
    careers = [c.strip() for c in re.split(r'[;,]', interests) if c.strip()]
    if not careers:
        careers = ["General Career"]  # fallback if user didn't specify

    results = {}

    for career in careers:
        prompt = f"""
You are a career mentor for Indian students.

Student Profile:
- Interests: {interests}
- Skills: {skills or "Beginner"}
- Education Level: {education}
- Target Career: {career}

Task:
Create 3 ROADMAPS for this career:
1. dream_path: based fully on interests (ideal path).
2. skill_path: based on current skills (fallback realistic path).
3. hybrid_path: combining interests + skills.

Each roadmap must include:
- short_term: array of 3–5 clear steps (0–6 months)
- mid_term: array of 3–5 steps (6–18 months)
- long_term: array of 2–4 steps (2–3 years)
- progress: readiness % (0–100)
- badge: motivational string with one emoji

Output ONLY valid JSON with keys dream_path, skill_path, hybrid_path.
"""

        raw = _call_model(prompt, temperature=0.65, max_tokens=1200)

        fallback = {
            "dream_path": {
                "short_term": [f"Research about {career}", "Take beginner course", "Follow experts in this field"],
                "mid_term": [f"Do 2–3 projects related to {career}", "Find a mentor"],
                "long_term": [f"Work towards a role in {career}"],
                "progress": 25,
                "badge": "🌟 Dream Chaser"
            },
            "skill_path": {
                "short_term": [f"Apply your current skills ({skills or 'general skills'}) in small projects"],
                "mid_term": ["Take certification to strengthen skills", "Do freelance work"],
                "long_term": ["Enter jobs that use these skills"],
                "progress": 40,
                "badge": "💪 Skill Builder"
            },
            "hybrid_path": {
                "short_term": [f"Do a small project combining your skills and {career}"],
                "mid_term": ["Build portfolio mixing skills + interests", "Intern in crossover roles"],
                "long_term": [f"Transition into {career} role using both skills and passion"],
                "progress": 35,
                "badge": "⚡ Creative Blend"
            }
        }

        data = _safe_json(raw, fallback)

        # Ensure structure
        for key in ["dream_path", "skill_path", "hybrid_path"]:
            if key not in data:
                data[key] = fallback[key]
            # fix formatting (short_term, mid_term, long_term must be lists)
            for term in ["short_term", "mid_term", "long_term"]:
                val = data[key].get(term, [])
                if isinstance(val, str):
                    data[key][term] = [val]
                elif not isinstance(val, list):
                    data[key][term] = fallback[key][term]
            if "progress" not in data[key]:
                data[key]["progress"] = fallback[key]["progress"]
            if "badge" not in data[key]:
                data[key]["badge"] = fallback[key]["badge"]

        results[career] = data

    return results


# ------------------ Wrappers (for old app.py imports) ------------------ #
def generate_career_suggestions(interests, skills, education):
    """
    Returns list of career objects for results.html
    """
    all_maps = generate_all_roadmaps(interests, skills, education)
    return [{"name": c,
             "why_match": f"You mentioned {c} in your interests.",
             "desc": f"Personalized roadmap available for {c}."}
            for c in all_maps.keys()]


def generate_roadmap(career, interests="", skills="", education=""):
    """
    Returns roadmap dict for a single career.
    """
    all_maps = generate_all_roadmaps(interests, skills, education)
    return all_maps.get(career, {})
