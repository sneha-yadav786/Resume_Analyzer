from flask import Flask, render_template, request
import os
import PyPDF2
import re
import json
ALLOWED_EXTENSIONS = {'pdf'}


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# -------------------- TEXT CLEANING --------------------
def clean_text(text):
    text = text.lower()
    text = text.replace('\n', ' ')
    text = text.replace('•', ' ')
    text = text.replace(',', ' ')
    text = text.replace('-', ' ')
    return text


def load_roles():
    with open("roles.json", "r") as file:
        return json.load(file)

# -------------------- LOAD SKILLS DATASET --------------------
def load_skills():
    with open("skills.txt", "r", encoding="utf-8") as file:
        skills = file.read().splitlines()
    return [skill.lower() for skill in skills]

def normalize_skill(skill):
    return skill.replace(".", "").replace(" ", "").lower()


#def calculate_match_percentage(user_skills, role_skills):
    user_skills_norm = [normalize_skill(s) for s in user_skills]
    role_skills_norm = [normalize_skill(s) for s in role_skills]

    matched = []

    for i, skill in enumerate(role_skills_norm):
        if skill in user_skills_norm:
            matched.append(role_skills[i])  # original name

    match_percent = (len(matched) / len(role_skills)) * 100

    return round(match_percent, 2), matched


def get_missing_skills(role_skills, user_skills):
    return [skill for skill in role_skills if skill not in user_skills]

# -------------------- DATASET BASED EXTRACTION --------------------
def extract_skills_from_dataset(text):
    skills_list = load_skills()
    found_skills = []

    for skill in skills_list:
        # better matching (avoid partial match like sql in mysql)
        if f" {skill} " in f" {text} ":
            found_skills.append(skill)

    return found_skills


# -------------------- REGEX BASED GUESS --------------------
def guess_skills(text):
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]+\b', text.lower())

    stopwords = {
        "i","and","the","is","in","on","at","a","to","for","of","with","by",
        "an","this","that","it","as","are","was","be","or","from",
        "name","resume","email","phone","address","india","school",
        "college","university","student","project","experience",
        "internship","training","certificate","certification",
        "month","january","february","march","april","may","june",
        "july","august","september","october","november","december"
    }

    filtered = [word for word in words if word not in stopwords]

    return filtered


# -------------------- ROUTES --------------------
@app.route('/')
def home():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_section(text, keyword):
    text = text.lower()
    if keyword in text:
        return text.split(keyword)[1][:500]
    return ""
def evaluate_projects(text):
    score = 0

    strong_words = ["developed", "built", "designed", "implemented","launched","engineered","constructed","integrated","earned","%","users","+","collaborated","optimized"]
    tech_words = ["react", "nodejs", "ml", "api", "docker","nextjs", "aws", "mern"]

    for word in strong_words:
        if word in text:
            score += 2

    for tech in tech_words:
        if tech in text:
            score += 3

    return score
def evaluate_experience(text):
    score = 0

    if "intern" in text:
        score += 5
    if "worked" in text:
        score += 5
    if "year" in text:
        score += 5

    return score
import re

def detect_impact(text):
    numbers = re.findall(r'\d+', text)
    return min(len(numbers) * 2, 10)
def final_score(skills, text):
    score = 0

    # skills relevance
    score += len(skills) * 2

    # project quality
    score += evaluate_projects(text)

    # experience
    score += evaluate_experience(text)

    # impact
    score += detect_impact(text)

    return min(score, 100)
def get_feedback(score):
    if score>=90:
        " Outstanding Profile 🔥 high chances to select 👍"

    elif score >= 85:
        return "Good condidate."
    elif score >= 70:
        return "Better Candidate 💪 But need some improvement."
    elif score >= 50:
        return "Average Profile ⚠️ Improve projects & experience."
    else:
        return "Weak Profile ❌ Needs improvement."



@app.route('/upload', methods=['POST'])
def upload_file():
    
    if 'resume' not in request.files:
        return "No file uploaded"

    file = request.files['resume']

    if file.filename == '':
        return "No selected file"
    
    if not allowed_file(file.filename):
        return "<h3 style='color:red;'>Invalid file type! Please upload a PDF resume.</h3>"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    role = request.form.get("role", "").strip().lower()
    roles = {k.lower(): v for k, v in load_roles().items()}

    # -------- PDF TEXT --------
    text = ""
    with open(filepath, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    cleaned_text = clean_text(text)

    final_skills = extract_skills_from_dataset(cleaned_text)
    display_skills = final_skills if final_skills else ["No skill detected"]

    if role in roles:
        role_skills = roles[role]
        missing_skills = get_missing_skills(role_skills, final_skills)

    else:
        suggestions = list(roles.keys())[:5]
        missing_skills = [", ".join(suggestions)]
        
    score = final_score(final_skills, cleaned_text)

    feedback = get_feedback(score)

    # breakdown
    project_score = evaluate_projects(cleaned_text)
    experience_score = evaluate_experience(cleaned_text)
    impact_score = detect_impact(cleaned_text)

    # -------- OUTPUT --------
    return render_template(
    "result.html",
    role=role.title(),
    score=score,
    feedback=feedback,
    matched_skills=display_skills,
    missing_skills=missing_skills,
    final_skills=display_skills
)
    

    

   


   
   

    
    
   

if __name__ == '__main__':
    app.run(debug=True)