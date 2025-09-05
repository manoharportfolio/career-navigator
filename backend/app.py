import os
from flask import Flask, render_template, request, url_for
from backend.services import ai_service

# Initialize the Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handles the main page: showing the form (GET) and
    processing it to show career suggestions (POST).
    """
    if request.method == 'POST':
        # Get user input from the form
        interests = request.form.get('interests', '')
        skills = request.form.get('skills', '')
        education = request.form.get('education', 'School')

        # Generate career suggestions based on user input
        careers = ai_service.generate_career_suggestions(interests, skills, education)

        # Render the results page with the suggestions
        return render_template('results.html',
                               careers=careers,
                               interests=interests,
                               skills=skills,
                               education=education)

    # For a GET request, just show the main input form
    return render_template('index.html')


@app.route('/roadmap/<career_name>')
def roadmap(career_name):
    """
    Generates and displays the detailed roadmaps (Dream, Skill, Hybrid)
    for a specific career chosen by the user.
    """
    # Get original user inputs from URL parameters
    interests = request.args.get('interests', '')
    skills = request.args.get('skills', '')
    education = request.args.get('education', '')

    # Generate all three roadmaps for the selected career
    all_roadmaps = ai_service.generate_all_roadmaps(career_name, interests, skills, education)
    
    # The function returns a dictionary where the key is the career name.
    # We extract the roadmap data for our specific career.
    career_data = all_roadmaps.get(career_name, {})

    # Render the roadmap page with the detailed data
    return render_template('roadmap.html',
                           career=career_name,
                           roadmaps=career_data)

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True, port=int(os.environ.get('PORT', 8080)))