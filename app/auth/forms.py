from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(Form):
    name = StringField('昵称', validators=[DataRequired(), Length(1, 16)])
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 32)])
    confirm = PasswordField('密码确认',
                            validators=[DataRequired(),
                                        EqualTo('password',
                                                message='两次输入的密码必须相同')])


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    rememberMe = BooleanField('记住我')
