from projects import app
from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View
nav = Nav()


@nav.navigation()
def nav_bar():
    navbar = list(Navbar(
        View('{title} Projects'.format(title=app.config['TITLE']),
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

    return Navbar('{title} Projects'.format(title=app.config['TITLE']),
                  *navbar)


nav.init_app(app)
