import os
import unittest
import io
import json
import datetime
from bcrypt import hashpw, gensalt
from flask import g
from projects import app
from projects.models import Project, User


libsum = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    " Maecenas semper tortor justo. Vivamus pretium quis leo quis "
    "posuere. In tristique orci ac orci laoreet, in imperdiet elit "
    "semper. Nam id eros gravida, fringilla nisl a, laoreet nibh. "
    "Mauris viverra, risus posuere pellentesque blandit, "
    "ipsum augue dignissim mi, vitae consectetur magna libero eu purus."
    " Interdum et malesuada fames ac ante ipsum primis in faucibus."
    " Ut sagittis bibendum nulla, et malesuada erat ultricies vel."
    " Duis vitae nisi augue. In blandit, purus ut consectetur suscipit,"
    " erat quam euismod nibh, gravida vestibulum purus velit nec libero"
    ". Nullam blandit auctor dolor in pretium. Nulla posuere magna non"
    " neque malesuada, tempor interdum metus aliquam. Nam tincidunt"
    " pellentesque congue. Duis auctor, tellus sit amet vehicula"
    " tempus, nunc purus ultrices lacus, nec convallis turpis nunc id"
    " purus. Cras aliquet dapibus convallis. Fusce fermentum velit enim"
    ", eu cursus enim fermentum at."
)


class Test_ProjectsTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        folders = {}
        folders["DATA_FOLDER"] = app.config["DATA_FOLDER"] = os.path.join(
            os.getcwd(), "tests/data"
        )

        folders["UPLOAD_FOLDER"] = app.config["UPLOAD_FOLDER"] = os.path.join(
            os.getcwd(), "tests/images"
        )
        app.config["WTF_CSRF_ENABLED"] = True
        # Create required folders for the application if they don't exist
        for _, folder in folders.items():
            try:
                os.makedirs(folder)
                print("Created: " + folder)
            except FileExistsError:
                pass

        # Override default DB setting ->use a testing db instead of the default
        app.config["DB"] = os.path.join(app.config["DATA_FOLDER"], "fair_test")
        self.username = "test@test.com"
        self.password = "test"
        user = User.get_with_first("email", self.username)
        hashed_pw = hashpw(bytes(self.password, "utf-8"), gensalt())

        if user is None:
            user = User(
                email=self.username,
                password=hashed_pw,
                projects=[],
                is_active=True,
                is_authenticated=True,
                is_anonymous=False,
                confirmed_on=datetime.datetime.now(),
            )
            user.save()
        self.user = user

        self.client = app.test_client()
        # Setup valid token
        self.csrf_token = None
        with self.client as client:
            resp = client.get("/index")
            assert resp.status_code == 200
            self.csrf_token = g.csrf_token

    def tearDown(self):
        # Clean up
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)

    def login(self, client):
        token_data = {"csrf_token": self.csrf_token}
        login_data = {"email": self.username, "password": self.password}
        login_data.update(token_data)
        login_resp = client.post("/login", data=login_data, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)

    def register_project(self, csrf_token, **kwargs):
        data = dict(csrf_token=csrf_token)
        data.update(kwargs)
        return self.client.post("/create_project", data=data, follow_redirects=True,)

    def tag_post_query(self, tag):
        return self.client.post(
            "/search", data=dict(tag=tag, csrf_token=self.csrf_token)
        )

    def tag_get_query(self, tag):
        return self.client.get("/tag?tag=" + tag)

    def test_register_data_render(self):
        # Auth check
        with self.client as client:
            create_resp = client.get("/create_project", follow_redirects=True)
            test_response = "Please log in to access this page."
            self.assertIn(bytes(test_response, encoding="utf8"), create_resp.data)
            # setup csrf_token
            token_data = {"csrf_token": self.csrf_token}
            self.login(client)
            create_resp = client.get(
                "create_project", data=token_data, follow_redirects=True
            )
            test_response = "Register a Project"
            self.assertIn(bytes(test_response, encoding="utf8"), create_resp.data)

    # TODO -> improve image validation by comparing hash of initial
    # and uploaded image, not just the returned page
    def test_web_upload_project(self):
        # Register project
        image_name = "robo_test_image.png"
        image_path = os.path.join(os.path.dirname(__file__), "images", image_name)
        with open(image_path, "rb") as img:
            image = img.read()

        with self.client as client:
            self.login(client)
            rv = self.register_project(
                name="My Awesome project",
                description=libsum,
                tags="Robots,Evolution",
                image=(io.BytesIO(image), image_name),
                csrf_token=self.csrf_token,
            )

            test_response = (
                "Your submission has been received, " "your metadata can be found at:"
            )
            self.assertIn(bytes(test_response, encoding="utf8"), rv.data)

    def test_web_upload_project_ten(self):
        # upload 10
        iterations = 10
        with self.client as client:
            self.login(client)

            image_name = "roborobo_simulation.png"
            image_path = os.path.join(os.path.dirname(__file__), "images", image_name)
            with open(image_path, "rb") as img:
                image = img.read()

            for _ in range(iterations):
                rv = self.register_project(
                    name="My Awesome project",
                    description=libsum,
                    tags="AnotherTag",
                    image=(io.BytesIO(image), image_name),
                    csrf_token=self.csrf_token,
                )

                test_response = (
                    "Your submission has been received, "
                    "your metadata can be found at:"
                )
                self.assertIn(bytes(test_response, encoding="utf8"), rv.data)

    def test_project_save_with_orcid(self):
        with self.client as client:
            # Authenticate
            self.login(client)

            image_name = "robo_test_image.png"
            image_path = os.path.join(os.path.dirname(__file__), "images", image_name)
            with open(image_path, "rb") as img:
                image = img.read()

            rv = self.register_project(
                name="My Awesome project",
                description=libsum,
                tags="Robots,Evolution,Individual Learning",
                image=(io.BytesIO(image), image_name),
                csrf_token=self.csrf_token,
            )

            test_response = (
                "Your submission has been received, " "your metadata can be found at:"
            )
            self.assertIn(bytes(test_response, encoding="utf8"), rv.data)

            # Clean up
            Project.clear()
            self.assertTrue(len(Project.get_all()) == 0)

    def test_project_save(self):
        project = Project(
            name="nasiodas",
            description="sdifosdfios",
            image="/Usdufsi/sdfs.png",
            tags="sdfo,sdfo,sdf",
        )
        project_id = project.save()
        new_project = Project.get(project_id)
        [
            self.assertEqual(project.__dict__[key], new_project.__dict__[key])
            for key in project.__dict__.keys()
        ]

    def test_project_update(self):
        # Pre cleanup
        self.user.projects.clear()
        self.user.save()
        # Save a new project
        project = Project(
            name="nasiodas",
            description="sdifosdfios",
            image=os.path.join("Usdufsi", "sdfs.png"),
            tags="sdfo,sdfo,sdf",
        )
        project_id = project.save()
        new_project = Project.get(project_id)
        [
            self.assertEqual(project.__dict__[key], new_project.__dict__[key])
            for key in project.__dict__.keys()
        ]

        # Authenticate
        with self.client as client:
            self.login(client)
            # Update project without being the correct owner
            new_data = {
                "name": "My Awesome project",
                "description": "nice_description",
                "tags": "Robots,Evolution,Individual Learning",
                "image": os.path.join("sdfsfs", "sdfsf.png"),
                "csrf_token": self.csrf_token,
            }
            rv = client.post(
                "/update/" + project_id, data=new_data, follow_redirects=True
            )
            test_response = "Your trying to update an entity that"
            self.assertIn(bytes(test_response, encoding="utf8"), rv.data)
            self.user.projects.append(project_id)
            self.user.save()
            rv = client.post(
                "/update/" + project_id, data=new_data, follow_redirects=True
            )
            test_response = "Update Success, your data can be found at: "
            self.assertIn(bytes(test_response, encoding="utf8"), rv.data)

    def test_project_getall_clear(self):
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)
        num_project = 10
        for _ in range(num_project):
            project = Project(
                name="nasiodas",
                description="sdifosdfios",
                image=os.path.join("Usdufsi", "sdfs.png"),
                tags="sdfo,sdfo,sdf",
            )
            project.save()
        self.assertEqual(len(Project.get_all()), num_project)

    # Tests whether a list of submitted projects with tags are
    # properly returned when search for with the post request (Search Bar)
    def test_tag_post_search(self):
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)

        first_tag = "eScience:bohrium:tests"
        second_tag = "eScience:bohrium:benchmark"
        num_project = 10
        for num in range(num_project):
            if num % 2 == 0:
                project = Project(
                    name="nasiodas",
                    description="sdifosdfios",
                    image=os.path.join("Usdufsi", "sdfs.png"),
                    tags=first_tag,
                )
            else:
                project = Project(
                    name="nasiodas",
                    description="sdifosdfios",
                    image=os.path.join("Usdufsi", "sdfs.png"),
                    tags=second_tag,
                )
            project.save()

        # Test Post Search -> json response evaluated
        first_query = json.loads(
            self.tag_post_query(tag=first_tag).get_data(as_text=True)
        )
        for project in first_query["data"]:
            self.assertTrue(project["tags"] == first_tag)

        second_query = json.loads(
            self.tag_post_query(tag=second_tag).get_data(as_text=True)
        )
        for project in second_query["data"]:
            # TODO -> test URL GET search query
            self.assertTrue(project["tags"] == second_tag)


if __name__ == "__main__":
    unittest.main()
