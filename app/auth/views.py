from flask import (redirect, url_for, flash, render_template,
                   request, abort, Blueprint)
from flask_login import login_user, login_required, current_user, logout_user
from .forms import RegisterForm, LoginForm
from .utility import (sendConfirmRegisteEmail, unconfirmedRequired,
                      next_is_valid)
from ..models import User, db


auth = Blueprint('auth', __name__, template_folder="templates")


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
    registerForm = RegisterForm()
    if registerForm.validate_on_submit():
        user = User.createAUser(name=registerForm.name.data,
                                email=registerForm.email.data,
                                password=registerForm.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        token = user.generateConfirmToken()
        sendConfirmRegisteEmail(user, token)
        flash('确认注册邮件已发送至您的邮箱，请确认注册！')
        print('register done!')
        return redirect(url_for('.waitConfirm'))
    return render_template('auth/loginAndRegister.html',
                           registerForm=registerForm, loginForm=LoginForm())


@auth.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user and user.checkPassword(loginForm.password.data):
            login_user(user, remember=loginForm.rememberMe.data)
            next = request.args.get('next')
            if not next_is_valid(next):
                return abort(400)
            return redirect(next or url_for('main.index'))
        flash('用户名或密码错误！')

    return render_template('auth/loginAndRegister.html', loginForm=loginForm,
                           registerForm=RegisterForm(), login=True)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已推出登录！')
    return redirect(url_for('main.index'))
