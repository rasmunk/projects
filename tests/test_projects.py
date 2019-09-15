import unittest
import os
from projects import app
from projects.models import Project
from projects.conf import config


class FairTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True

        # Required folders
        folders = {}
        folders['DATA_FOLDER'] = app.config['DATA_FOLDER'] = os.path.join(
            os.getcwd(), "data")
        folders['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] = os.path.join(
            os.getcwd(), "images")
        # Create required folders for the application if they don't exist
        for key, folder in folders.items():
            try:
                os.makedirs(folder)
                print("Created: " + folder)
            except FileExistsError:
                pass

        app.config['WTF_CSRF_ENABLED'] = False
        # Override default DB setting
        # -> use a testing db instead of the default
        app.config['DB'] = os.path.join(app.config['DATA_FOLDER'],
                                        "dataset_test")
        self.app = app.test_client()

    def tearDown(self):
        # Clean up
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)

    def test_dummy(self):
        self.assertTrue(True)

    def create_user(self):
        pass


if __name__ == '__main__':
    unittest.main()
