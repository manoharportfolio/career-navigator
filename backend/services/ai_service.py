import os
import json
import re
import time
from dotenv import load_dotenv

# Import the specific exception for retrying
from google.api_core import exceptions

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


def _call_model(prompt, temperature=0.6, max_tokens=1500):
    """
    Generic function to call the generative model with automatic retries.
    """
    delay = 1  # Initial delay in seconds
    for i in range(5):  # Try up to 5 times
        try:
            resp = _model.generate_content(
                [prompt],
                generation_config=GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return (resp.text or "").strip()
        except exceptions.ResourceExhausted as e:
            print(f"ResourceExhausted, retrying in {delay} seconds... ({e})")
            time.sleep(delay)
            delay *= 2  # Double the delay for the next retry
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "" # Return empty on other errors
    
    print("Failed to get response after multiple retries.")
    return "" # Return empty if all retries fail


def generate_career_suggestions(interests, skills, education):
    """
    Efficiently generates a list of 3-5 career suggestions without creating
    full roadmaps upfront.
    Returns a list of career objects for results.html.
    """
    prompt = f"""
    You are a career mentor for Indian students.
    Based on the following profile, suggest 3 to 5 relevant career paths.

    Student Profile:
    - Interests: {interests}
    - Skills: {skills or "Beginner"}
    - Education Level: {education}

    Task:
    Provide a brief, one-sentence description for why each career is a good match.
    Output ONLY a JSON array of objects, where each object has keys "name", "desc".
    Example format: [{{"name": "Data Scientist", "desc": "A great fit for your interest in coding and analytics."}}]
    """
    raw = _call_model(prompt, temperature=0.5, max_tokens=500)
    
    # This fallback is now dynamic and uses your input
    # Safely get the first interest, or provide a default
    first_interest = interests.split(',')[0].strip() if interests else "your interests"
    
    fallback = [
        {"name": f"Specialist in {first_interest.title()}", "desc": f"A role focused on your primary interest in {first_interest}."},
        {"name": "Project Coordinator", "desc": "A versatile role where you can apply your skills to projects you're passionate about."},
        {"name": "Digital Marketer", "desc": "Combines creativity with business acumen, adaptable to many interests."}
    ]
    
    return _safe_json(raw, fallback)


def generate_all_roadmaps(career, interests="", skills="", education=""):
    """
    Generates three detailed roadmaps (dream, skill, hybrid) for a SINGLE target career.
    Returns a dictionary with roadmaps for that one career.
    """
    prompt = f"""
    You are a career mentor for Indian students.

    Student Profile:
    - Interests: {interests}
    - Skills: {skills or "Beginner"}
    - Education Level: {education}
    - Target Career: {career}

    Task:
    Create 3 distinct ROADMAPS for the student to achieve their target career:
    1. dream_path: An ideal path based purely on their interests.
    2. skill_path: A practical path that leverages their current skills.
    3. hybrid_path: A balanced path combining both interests and skills.

    For each of the 3 roadmaps, you must include:
    - short_term: An array of 3-5 clear, actionable steps for the next 0-6 months.
    - mid_term: An array of 3-5 actionable steps for the next 6-18 months.
    - long_term: An array of 2-4 actionable steps for the next 2-3 years.
    - progress: An integer (0-100) representing the student's current readiness for this path.
    - badge: A short, motivational string with one relevant emoji.

    Output a single JSON object with keys "dream_path", "skill_path", and "hybrid_path" ONLY.
    Do not include any other text or markdown formatting.
    """
    raw = _call_model(prompt, temperature=0.65, max_tokens=1500)
    
    fallback = {
        "dream_path": {
            "short_term": [f"Research foundational concepts of {career}", "Take a beginner's online course", "Follow industry experts on social media"],
            "mid_term": [f"Complete 2-3 small projects related to {career}", "Find a mentor in the field"],
            "long_term": [f"Build a strong portfolio and start applying for internships or junior roles in {career}"],
            "progress": 25,
            "badge": "🌟 Dream Chaser"
        },
        "skill_path": {
            "short_term": [f"Apply your current skills ({skills or 'general skills'}) to projects relevant to {career}"],
            "mid_term": ["Earn a certification to validate your existing skills", "Look for freelance opportunities"],
            "long_term": ["Target job roles that are a stepping stone to your desired career"],
            "progress": 40,
            "badge": "💪 Skill Builder"
        },
        "hybrid_path": {
            "short_term": [f"Start a project that combines your interest in {career} with your skills in {skills or 'your current abilities'}"],
            "mid_term": ["Build a unique portfolio showcasing this blend", "Seek internships in interdisciplinary roles"],
            "long_term": [f"Transition into a specialized {career} role that values your unique skill combination"],
            "progress": 35,
            "badge": "⚡ Creative Blend"
        }
    }

    data = _safe_json(raw, fallback)
    results = {}

    # This loop ensures that the AI's output has the correct structure.
    for key in ["dream_path", "skill_path", "hybrid_path"]:
        if key not in data:
            data[key] = fallback[key]

        if "progress" not in data[key]:
            data[key]["progress"] = fallback[key]["progress"]
        if "badge" not in data[key]:
            data[key]["badge"] = fallback[key]["badge"]

        for term in ["short_term", "mid_term", "long_term"]:
            val = data[key].get(term, [])
            if isinstance(val, str):
                data[key][term] = [val]
            elif not isinstance(val, list):
                data[key][term] = fallback[key][term]

    results[career] = data
    return results