# http://flask.pocoo.org/docs/0.12/patterns/distribute/
import os
from setuptools import find_packages
from distutils.core import setup

cur_dir = os.path.abspath(os.path.dirname(__file__))

long_description = open('README.rst').read()

setup(
    name='projects-site',
    version='0.0.4',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
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
        'wtforms',
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
