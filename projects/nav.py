from flask_login import current_user
from flask_nav.elements import Navbar, View
from projects.conf import config
from projects import nav


@nav.navigation()
def nav_bar():
    navbar = list(Navbar(
        View('{} Projects'.format(config.get('PROJECTS', 'title')),
             '.projects'),
        View('Projects', '.projects'),
    ).items)
    if current_user.is_authenticated:
        navbar.extend([
            View('My Projects', '.my_projects'),
            View('Create Project', '.create'),
            View('Logout', '.logout'),
        ])
    else:
        navbar.extend([
            View('Login', '.login'),
        ])

    return Navbar('{} Projects'.format(config.get('PROJECTS', 'title')),
                  *navbar)
