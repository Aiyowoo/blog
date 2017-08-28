from flask_wtf import FlaskForm as Form
from wtforms import (StringField, PasswordField, BooleanField,
                     SubmitField, ValidationError)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from ..models import User


class RegisterForm(Form):
    name = StringField('昵称', validators=[DataRequired(), Length(1, 16)])
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 32)])
    confirm = PasswordField('密码确认',
                            validators=[DataRequired(),
                                        EqualTo('password',
                                                message='两次输入的密码必须相同')])

    def validate_email(form, field):
        if field.data and User.query.filter_by(email=field.data).count():
            raise ValidationError("邮箱已存在！")


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    rememberMe = BooleanField('记住我')
    submit = SubmitField('提交')
