from flask import request
from app import app
from model.user_model import user_model

obj = user_model()

@app.route('/upload', methods=['POST'])
def upload_resume_controller():
    file = request.files.get('resume')
    return obj.upload_resume_model(file)