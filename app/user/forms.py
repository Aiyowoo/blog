from flask_wtf import FlaskForm as Form
from flask_login import current_user
from wtforms import (StringField, PasswordField, ValidationError,
                     FileField, SubmitField)
from wtforms.validators import DataRequired, Length, EqualTo


class BaseInfoForm(Form):
    profilePicture = FileField('头像')
    name = StringField('昵称', validators=[DataRequired(), Length(1, 16)])
    introduction = StringField('简介')
    submit = SubmitField('确认修改')


class PasswordForm(Form):
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 16)])
    newPassword = PasswordField('新密码',
                                validators=[DataRequired(), Length(6, 32)])
    confirm = PasswordField('密码确认',
                            validators=[DataRequired(),
                                        EqualTo('password',
                                                message='两次输入的密码必须相同')])
    submit = SubmitField('确认修改')

    def validate_password(form, field):
        """

        检查原始密码是否输入正确

        """
        if field.data and (not current_user.checkPassword(field.data)):
            raise ValidationError('密码有误!')
