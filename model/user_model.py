import os

class user_model:
    def __init__(self):
        self.upload_folder = "uploads"

        # create folder if not exists
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def upload_resume_model(self, file):
        if not file:
            return {"msg": "No file provided"}

        # get file name
        filename = file.filename

        # define path
        filepath = os.path.join(self.upload_folder, filename)

        # save file
        file.save(filepath)

        return {
            "msg": "File uploaded successfully",
            "filename": filename
        }