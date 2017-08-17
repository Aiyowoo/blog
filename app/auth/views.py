from flask import (redirect, url_for, flash, render_template,
                   request, next_is_valid, abort)
from flask_login import login_user, login_required, current_user, logout_user
from . import auth
from .forms import RegisterForm, LoginForm
from .utility import (sendConfirmRegisteEmail, unconfirmedRequired)
from ..models import User
from .. import db


@auth.route('/confirm/<token>')
@login_required
@unconfirmedRequired
def confirm(token):
    if current_user.confirm(token):
        flash('您已成功完成邮箱验证！')
        return redirect(url_for('main.index'))
    flash('验证失败，请重新完成验证！')
    return redirect(url_for('.resendConfirmEmail'))


@auth.route('/waitConfirm')
@login_required
@unconfirmedRequired
def waitConfirm():
    return render_template('auth/waitConfirm.html')


@auth.route('/resendConfirmEmail')
@login_required
@unconfirmedRequired
def resendConfirmEmail():
    token = current_user.generateConfirmToken()
    sendConfirmRegisteEmail(current_user, token)
    flash('确认注册邮件已发送至您的邮箱，请确认注册！')
    return render_template('auth/waitConfirm.html')


@auth.route('/register', methods=['GET', 'POST'])
def userRegister():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.createAUser(name=form.name.data,
                                email=form.email.data,
                                password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        token = user.generateConfirmToken()
        sendConfirmRegisteEmail(user, token)
        flash('确认注册邮件已发送至您的邮箱，请确认注册！')
        return redirect(url_for('.waitConfirm'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).get()
        if user and user.checkPassword(form.password.data):
            login_user(user, remember=form.rememberMe.data)
            next = request.args.get('next')
            if not next_is_valid(next):
                return abort(400)
            return redirect(next or url_for('main.index'))

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已推出登录！')
    return redirect(url_for('main.index'))
