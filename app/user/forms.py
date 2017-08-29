from flask_wtf import FlaskForm as Form
from wtforms import (StringField, PasswordField, BooleanField,
                     SubmitField, ValidationError)
from wtforms.validators import DataRequired, Length, EqualTo


class BaseForm(Form):
    name = StringField('昵称', validators=[DataRequired(), Length(1, 16)])
