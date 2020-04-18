from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    FileField,
    SelectMultipleField,
    widgets,
    PasswordField,
)
from wtforms.validators import DataRequired, Regexp, Email, EqualTo, Length
from projects.conf import config


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DefaultProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    image = FileField(
        "Project Image",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png"], "Only JPG and PNG images are allowed"),
        ],
    )
    tags = StringField(
        "Tags",
        validators=[
            DataRequired(),
            Regexp(
                r"" + config.get("PROJECTS", "tags_regex"),
                message=config.get("PROJECTS", "tags_regex_msg"),
            ),
        ],
    )


class AuthRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address format"),
            Regexp(
                r"" + config.get("PROJECTS", "auth_regex_username"),
                message=config.get("PROJECTS", "auth_regex_msg"),
            ),
        ],
    )


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address format"),
            Regexp(
                r"" + config.get("PROJECTS", "auth_regex_username"),
                message=config.get("PROJECTS", "auth_regex_msg"),
            ),
        ],
    )


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address format"),
            Regexp(
                r"" + config.get("PROJECTS", "auth_regex_username"),
                message=config.get("PROJECTS", "auth_regex_msg"),
            ),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired()])
