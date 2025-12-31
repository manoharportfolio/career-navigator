# Career Navigator 🚀

An AI-powered career guidance tool that helps students discover suitable career paths and generates personalized, step-by-step roadmaps.  
No resume required — just enter your interests and skills to get clear guidance on what to learn, what projects to build, and which roles to aim for.

This project is designed to reduce confusion, remove guesswork, and give students a clear direction forward.

---

## ✨ Features
- Quick input (no resume required)
- Personalized career suggestions
- Step-by-step roadmap generation
- Visual progress tracker with badges

---

## 🛠️ Tech Stack
- Google Cloud Vertex AI  
- Backend: Flask / FastAPI  
- Frontend: Streamlit / React  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/manoharportfolio/career-navigator.git
cd career-navigator
```
### 2️⃣ Create and activate a virtual environment
Python 3.11 is required
```bash
py -3.11 -m venv .venv
source .venv/Scripts/activate
python --version
```
You should see:

    Python 3.11.x
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Run the application
```bash
python -m backend.app
```
### 📌 Important Notes
- Python 3.11 is mandatory for this project
(Newer versions like Python 3.13 may cause dependency issues, especially with NumPy and Pandas.)
- The .venv folder is intentionally ignored and should not be committed to Git.
- If you face installation errors, first verify your Python version using:
```bash
python --version
```
## 📜 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software for personal or commercial purposes, provided that the original copyright notice and license text are included.

See the [LICENSE](LICENSE) file for full details.

