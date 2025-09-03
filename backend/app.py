from flask import Flask, render_template, request
from services.ai_service import generate_career_suggestions, generate_roadmap

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        interests = request.form.get("interests", "")
        skills = request.form.get("skills", "")
        education = request.form.get("education", "College")

        careers = generate_career_suggestions(interests, skills, education)
        return render_template("results.html", careers=careers,
                               interests=interests, skills=skills, education=education)
    return render_template("index.html")


@app.route("/roadmap/<career_name>")
def roadmap(career_name):
    interests = request.args.get("interests", "")
    skills = request.args.get("skills", "")
    education = request.args.get("education", "College")

    roadmap = generate_roadmap(career_name, interests, skills, education)
    return render_template("roadmap.html", career=career_name, roadmap=roadmap)


if __name__ == "__main__":
    app.run(debug=True)
