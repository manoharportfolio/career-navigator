import os
import re
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel, GenerationConfig

# ------------------------------------------------
# Load environment variables
# ------------------------------------------------
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
MODEL = os.getenv("MODEL", "gemini-1.5-flash").strip('"').strip("'")
CRED_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ------------------------------------------------
# Force-load service account credentials
# ------------------------------------------------
if not CRED_PATH or not os.path.exists(CRED_PATH):
    raise FileNotFoundError(f"❌ Service account key not found at {CRED_PATH}")

credentials = service_account.Credentials.from_service_account_file(CRED_PATH)

vertex_init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

print(f"✅ Vertex AI initialized with project={PROJECT_ID}, location={LOCATION}, creds={CRED_PATH}")

# ------------------------------------------------
# Global model instance
# ------------------------------------------------
_model = GenerativeModel(MODEL)


# ------------------------------------------------
# Helper: Call Gemini model
# ------------------------------------------------
def _call_model(prompt, temperature=0.6, max_tokens=1024):
    """Call Gemini model and return cleaned text output."""
    config = GenerationConfig(temperature=temperature, max_output_tokens=max_tokens)
    resp = _model.generate_content(prompt, generation_config=config)
    if not resp or not resp.candidates or not resp.candidates[0].content.parts:
        return "⚠️ No response from model."
    return resp.candidates[0].content.parts[0].text


# ------------------------------------------------
# Generate multiple roadmaps (interest-based, skill-based, combined)
# ------------------------------------------------
def generate_all_roadmaps(interests: str, skills: str, education: str):
    """
    Returns 3 types of career roadmaps:
    1. Based only on interests
    2. Based only on skills
    3. Based on both (combined)
    """

    prompt = f"""
    A student has the following:
    - Interests: {interests}
    - Skills: {skills}
    - Education: {education}

    Generate three separate career roadmap sets:

    1. **Interest-Based Roadmaps**
       For each interest mentioned, suggest possible careers and a step-by-step roadmap
       (short-term 0–6 months, mid-term 6–18 months, long-term 2–3 years).

    2. **Skill-Based Roadmaps**
       For each skill mentioned, suggest possible careers they can realistically pursue if
       their interests do not work out. Provide the same step-by-step roadmap.

    3. **Combined Roadmaps**
       Suggest careers that merge both their interests and skills (creative intersections).
       Provide the roadmap.

    Make sure to cover *all interests and skills individually*, not just 3 careers.
    Format output clearly as JSON with keys: "interest_based", "skill_based", "combined".
    """

    raw = _call_model(prompt, temperature=0.65, max_tokens=1800)

    # Try parsing into JSON safely
    try:
        cleaned = re.sub(r"```(json|JSON)?", "", raw).replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        return {"error": "Failed to parse model response", "raw_output": raw}


# ------------------------------------------------
# Public API for Flask
# ------------------------------------------------
def generate_career_suggestions(interests: str, skills: str, education: str):
    """Main function Flask calls: returns structured roadmaps."""
    all_maps = generate_all_roadmaps(interests, skills, education)
    return all_maps


def generate_roadmap(interests: str, skills: str, education: str):
    """Alias to maintain compatibility with app.py"""
    return generate_all_roadmaps(interests, skills, education)
