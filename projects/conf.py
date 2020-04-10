import os
from projects_base.base.conf import config

config.read(os.path.abspath("projects_base/res/config.ini"))
config.read(os.path.abspath("res/config.ini"))

# Required folders
folders = {}
folders["DATA_FOLDER"] = os.path.abspath(config.get("PROJECTS", "data_folder"))
folders["UPLOAD_FOLDER"] = os.path.abspath(config.get("PROJECTS", "upload_folder"))

# Create required folders for the application if they don't exist
for key, folder in folders.items():
    try:
        os.makedirs(folder)
        print("Created: " + folder)
    except FileExistsError:
        pass
