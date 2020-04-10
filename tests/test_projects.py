import os
import unittest
import io
import json
import datetime
from bcrypt import hashpw, gensalt
from flask import g
from projects import app
from projects.models import Project, User


libsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.' \
         ' Maecenas semper tortor justo. Vivamus pretium quis leo quis ' \
         'posuere. In tristique orci ac orci laoreet, in imperdiet elit ' \
         'semper. Nam id eros gravida, fringilla nisl a, laoreet nibh. ' \
         'Mauris viverra, risus posuere pellentesque blandit, ' \
         'ipsum augue dignissim mi, vitae consectetur magna libero eu purus.' \
         ' Interdum et malesuada fames ac ante ipsum primis in faucibus.' \
         ' Ut sagittis bibendum nulla, et malesuada erat ultricies vel.' \
         ' Duis vitae nisi augue. In blandit, purus ut consectetur suscipit,' \
         ' erat quam euismod nibh, gravida vestibulum purus velit nec libero' \
         '. Nullam blandit auctor dolor in pretium. Nulla posuere magna non' \
         ' neque malesuada, tempor interdum metus aliquam. Nam tincidunt' \
         ' pellentesque congue. Duis auctor, tellus sit amet vehicula' \
         ' tempus, nunc purus ultrices lacus, nec convallis turpis nunc id' \
         ' purus. Cras aliquet dapibus convallis. Fusce fermentum velit enim' \
         ', eu cursus enim fermentum at.'


class Test_ProjectsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        folders = {}
        folders['DATA_FOLDER'] = app.config[
            'DATA_FOLDER'] = os.path.join(os.getcwd(), "tests/data")

        folders['UPLOAD_FOLDER'] = app.config[
            'UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "tests/images")
        app.config['WTF_CSRF_ENABLED'] = True
        # Create required folders for the application if they don't exist
        for _, folder in folders.items():
            try:
                os.makedirs(folder)
                print("Created: " + folder)
            except FileExistsError:
                pass

        # Override default DB setting ->use a testing db instead of the default
        app.config['DB'] = os.path.join(app.config['DATA_FOLDER'],
                                        "fair_test")
        self.username = 'test@test.com'
        self.password = 'test'
        user = User.get_with_first('email', self.username)
        if user is None:
            user = User(email=self.username,
                        password=hashpw(bytes(self.password, 'utf-8'), gensalt()),
                        datasets=[],
                        is_active=True,
                        is_authenticated=True,
                        is_anonymous=False,
                        confirmed_on=datetime.datetime.now())
            user.save()
        self.user = user

        self.client = app.test_client()
        # Setup valid token
        self.csrf_token = None
        with self.client as client:
            resp = client.get('/index')
            assert resp.status_code == 200
            self.csrf_token = g.csrf_token


    def tearDown(self):
        # Clean up
        Project.clear()
        self.assertTrue(len(Project.get_all()) == 0)

    def test_register_data_render(self):
        # Auth check
        with self.client as client:
            create_resp = client.get('/create_project', follow_redirects=True)
            test_response = 'Please log in to access this page.'
            self.assertIn(bytes(test_response, encoding='utf8'), create_resp.data)
            # setup csrf_token
            token_data = {'csrf_token': self.csrf_token}
            login_data = {'email': self.username,
                          'password': self.password}
            login_data.update(token_data)

            login_resp = client.post('/login', data=login_data, follow_redirects=True)
            self.assertEqual(login_resp.status_code, 200)
            create_resp = client.get('create_project', data=login_data, follow_redirects=True)
            test_response = "Register a Project"
            self.assertIn(bytes(test_response, encoding='utf8'), create_resp.data)

    def register_dataset(self, name, description, doi, date, sci_area,
                         references, tags, image, orcid, csrf_token):
        return self.client.post('/create_project', data=dict(
            name=name,
            description=description,
            doi=doi,
            date=date,
            sci_area=sci_area,
            references=references,
            tags=tags,
            image=image,
            orcid=orcid,
            csrf_token=csrf_token
        ), follow_redirects=True)

    def tag_post_query(self, tag):
        return self.client.post('/search', data=dict(
            tag=tag,
            csrf_token=self.csrf_token
        ))

    def tag_get_query(self, tag):
        return self.client.get("/tag?tag=" + tag)

    # # TODO -> improve image validation by comparing hash of initial
    # # and uploaded image, not just the returned page
    # def test_web_upload_dataset(self):
    #     # Register dataset
    #     image_name = "robo_test_image.png"
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    #     with open(image_path, 'rb') as img:
    #         image = img.read()

    #     # Authenticate
    #     self.app.post('/login', data={'csrf_token': self.csrf_token})

    #     rv = self.register_dataset(name='My Awesome Dataset',
    #                                description=libsum,
    #                                doi='https://doi.org'
    #                                    '/10.1145/3067695.3082550',
    #                                date='2017-09-08',
    #                                sci_area='eScience',
    #                                references='Hart Emma, Paecther Ben, '
    #                                           'Heinerman',
    #                                tags='Robots,Evolution',
    #                                image=(io.BytesIO(image), image_name),
    #                                orcid="",
    #                                csrf_token=self.csrf_token)

    #     test_response = "Your submission has been received, " \
    #                     "your metadata can be found at:"
    #     self.assertIn(bytes(test_response, encoding='utf8'), rv.data)

    # def test_web_upload_dataset_ten(self):
    #     # Authenticate
    #     self.app.post('/login', data={'csrf_token': self.csrf_token})

    #     # upload 10
    #     iterations = 10
    #     image_name = "roborobo_simulation.png"
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    #     with open(image_path, 'rb') as img:
    #         image = img.read()

    #     for dataset in range(iterations):
    #         rv = self.register_dataset(name='My Awesome Dataset',
    #                                    description=libsum,
    #                                    doi='https://doi.org'
    #                                        '/10.1145/3067695.3082550',
    #                                    date='2017-09-08',
    #                                    sci_area='eScience',
    #                                    references='Hart Emma, Paecther Ben, '
    #                                               'Heinerman',
    #                                    tags='Robots,Evolution,'
    #                                         'Individual Learning',
    #                                    image=(io.BytesIO(image), image_name),
    #                                    orcid="",
    #                                    csrf_token=self.csrf_token)

    #         test_response = "Your submission has been received, " \
    #                         "your metadata can be found at:"
    #         self.assertIn(bytes(test_response, encoding='utf8'), rv.data)

    # def test_dataset_save_with_orcid(self):
    #     # Authenticate
    #     self.app.post('/login', data={'csrf_token': self.csrf_token})

    #     image_name = "robo_test_image.png"
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    #     with open(image_path, 'rb') as img:
    #         image = img.read()

    #     rv = self.register_dataset(name='My Awesome Dataset',
    #                                description=libsum,
    #                                doi='https://doi.org'
    #                                    '/10.1145/3067695.3082550',
    #                                date='2017-09-08',
    #                                sci_area='eScience',
    #                                references='Hart Emma, Paecther Ben, '
    #                                           'Heinerman',
    #                                tags='Robots,Evolution,Individual Learning',
    #                                image=(io.BytesIO(image), image_name),
    #                                orcid="3293-3043-2003-2032",
    #                                csrf_token=self.csrf_token)

    #     test_response = "Your submission has been received, " \
    #                     "your metadata can be found at:"
    #     self.assertIn(bytes(test_response, encoding='utf8'), rv.data)

    #     # Clean up
    #     Project.clear()
    #     self.assertTrue(len(Project.get_all()) == 0)

    # def test_dataset_save(self):
    #     dataset = Project(doi='sdfsdf', sci_area='gdfuiort',
    #                           name='nasiodas', references='iwerowr',
    #                           description='sdifosdfios',
    #                           image='/Usdufsi/sdfs.png', tags='sdfo,sdfo,sdf')
    #     dataset_id = dataset.save()
    #     new_dataset = Project.get(dataset_id)
    #     [self.assertEqual(dataset.__dict__[key], new_dataset.__dict__[key])
    #      for key in dataset.__dict__.keys()]

    # def test_dataset_update(self):
    #     # Pre cleanup
    #     self.user.datasets.clear()
    #     self.user.save()
    #     # Save a new dataset
    #     dataset = Project(doi='sdfsdf', sci_area='gdfuiort',
    #                           name='nasiodas', references='iwerowr',
    #                           description='sdifosdfios',
    #                           image='/Usdufsi/sdfs.png', tags='sdfo,sdfo,sdf')
    #     dataset_id = dataset.save()
    #     new_dataset = Project.get(dataset_id)
    #     [self.assertEqual(dataset.__dict__[key], new_dataset.__dict__[key])
    #      for key in dataset.__dict__.keys()]
    #     # Authenticate
    #     self.app.post('/login', data={'csrf_token': self.csrf_token})
    #     # Update dataset without being the correct owner
    #     new_data = {'name': 'My Awesome Dataset',
    #                 'description': 'nice_description',
    #                 'doi': 'https://doi.org/10.1145/3067695.3082550',
    #                 'date': '2017-09-08',
    #                 'sci_area': 'eScience',
    #                 'references': 'Hart Emma, Paecther Ben, Heinerman',
    #                 'tags': 'Robots,Evolution,Individual Learning',
    #                 'image': '/sdfsfs/sdfsf.png',
    #                 'orcid': "3293-3043-2003-2032",
    #                 'csrf_token': self.csrf_token}
    #     rv = self.app.post("/update/" + dataset_id, data=new_data,
    #                        follow_redirects=True)
    #     test_response = "Your trying to update a dataset thats not yours"
    #     self.assertIn(bytes(test_response, encoding='utf8'), rv.data)
    #     self.user.datasets.append(dataset_id)
    #     self.user.save()
    #     rv = self.app.post("/update/" + dataset_id, data=new_data,
    #                        follow_redirects=True)
    #     test_response = "Update Success, your data can be found at: "
    #     self.assertIn(bytes(test_response, encoding='utf8'), rv.data)

    # def test_dataset_getall_clear(self):
    #     Project.clear()
    #     self.assertTrue(len(Project.get_all()) == 0)
    #     num_dataset = 10
    #     for num in range(num_dataset):
    #         dataset = Project(doi=str(num), sci_area='gdfuiort',
    #                               name='nasiodas', references='iwerowr',
    #                               description='sdifosdfios',
    #                               image='/Usdufsi/sdfs.png',
    #                               tags='sdfo,sdfo,sdf')
    #         dataset.save()

    #     self.assertEqual(len(Project.get_all()), num_dataset)

    # # Tests whether a list of submitted Datasets with tags are
    # # properly returned when search for with the post request (Search Bar)
    # def test_tag_post_search(self):
    #     Project.clear()
    #     self.assertTrue(len(Project.get_all()) == 0)

    #     first_tag = 'eScience:bohrium:tests'
    #     second_tag = 'eScience:bohrium:benchmark'
    #     num_dataset = 10
    #     for num in range(num_dataset):
    #         if num % 2 == 0:
    #             dataset = Project(doi=str(num), sci_area='gdfuiort',
    #                                   name='nasiodas',
    #                                   references='iwerowr',
    #                                   description='sdifosdfios',
    #                                   image='/Usdufsi/sdfs.png',
    #                                   tags=first_tag)
    #         else:
    #             dataset = Project(doi=str(num), sci_area='gdfuiort',
    #                                   name='nasiodas',
    #                                   references='iwerowr',
    #                                   description='sdifosdfios',
    #                                   image='/Usdufsi/sdfs.png',
    #                                   tags=second_tag)
    #         dataset.save()

    #     # Test Post Search -> json response evaluated
    #     first_query = json.loads(
    #         self.tag_post_query(tag=first_tag)
    #             .get_data(as_text=True))
    #     for dataset in first_query['data']:
    #         self.assertTrue(dataset['tags'] == first_tag)

    #     second_query = json.loads(
    #         self.tag_post_query(tag=second_tag)
    #             .get_data(as_text=True))
    #     for dataset in second_query['data']:
    #         # TODO -> test URL GET search query
    #         self.assertTrue(dataset['tags'] == second_tag)

    # # Test Erda import parsers
    # def test_erda_import(self):
    #     legacy_data = {'name': 'Rasmus', 'description': 'Rasmus test',
    #                    'date': '2017-09-08'}
    #     pre_tag_data = {'name': 'Rasmus_Pre_Tag_Archive_test',
    #                     'description': libsum,
    #                     'date': '2018-02-16'}
    #     # Authenticate
    #     data = {'csrf_token': self.csrf_token}
    #     self.app.post('/login', data=data)
    #     # Render create dataset page
    #     legacy_import_rv = json.loads(self.erda_import_query(
    #         erda_url='https://erda.dk/public/archives'
    #                  '/YXJjaGl2ZS05dHRxRVU='
    #                  '/published-archive.html')
    #                                   .get_data(as_text=True))
    #     self.maxDiff = None
    #     self.assertEqual(legacy_data, legacy_import_rv['data'])

    #     pre_tag_import = json.loads(self.erda_import_query(
    #         erda_url='http://www.erda.dk/public/archives'
    #                  '/YXJjaGl2ZS1xOXdiNzc=/published-archive.html')
    #         .get_data(as_text=True))
    #     self.assertEqual(pre_tag_data, pre_tag_import['data'])


if __name__ == '__main__':
    unittest.main()