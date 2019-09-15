from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Optional, Regexp


class TagsSearchForm(FlaskForm):
    tag = StringField('Tags Search',
                      validators=[Optional(),
                                  Regexp(r'^[\w,:_\-* ]*$',
                                         message="Allowed tag characters "
                                                 "include letters spaces and"
                                                 ", : _ - *")])
