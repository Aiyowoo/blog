from flask import flash, redirect, url_for
from functools import wraps
from flask_login import current_user
from ..email import sendMail


def sendConfirmRegisteEmail(user, token):
    sendMail(user.email, '注册确认', 'email/auth/confirm.html',
             user=user, token=token)


def unconfirmedRequired(func):
    """

    装饰视图函数，确保以验证的用户不再访问相关的视图
    该视图函数应同时被login_required装饰

    """
    @wraps(func)
    def wrappedFunc(*args, **kwargs):
        if current_user.confirmed:
            flash('您已通过验证，无需再次验证！')
            return redirect(url_for('main.index'))
        func(*args, **kwargs)
    return wrappedFunc
