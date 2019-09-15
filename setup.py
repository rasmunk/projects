# http://flask.pocoo.org/docs/0.12/patterns/distribute/
import os
from setuptools import find_packages
from distutils.core import setup

cur_dir = os.path.abspath(os.path.dirname(__file__))

# Get the current package version.
version_ns = {}
with open(os.path.join(cur_dir, 'version.py')) as f:
    exec(f.read(), {}, version_ns)


long_description = open('README.rst').read()

setup(
    name='projects-site',
    version=version_ns['__version__'],
    long_description=long_description,
    description="""
                A website template for hosting project
                metadata information via flask
                """,
    url='https://github.com/rasmunk/projects-site',
    author='Rasmus Munk',
    author_email='rasmus.munk@nbi.ku.dk',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=['Website', 'Flask', 'MetaData'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'flask-bootstrap',
        'flask-nav',
        'flask_wtf',
        'WTForms',
        'requests',
        'wtforms-components',
        'flask_login',
        'flask_mail',
        'bcrypt',
        'configparser'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
