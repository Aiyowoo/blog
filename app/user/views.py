from flask import Blueprint, render_template
from flask_login import login_required, current_user, request
from .logger import logger
from ..utility import exceptionHandler


user = Blueprint('user', __name__, template_folder='templates')


@user.route('/homepage/<int:userId>')
@exceptionHandler(logger, "can't access to user homepage")
def home(userId):
    """

    用户主页，是否登录均可访问

    """
    user = User.query.get_or_404(userId)
    return render_template('user/home.html', user=user)


@user.route('/setting')
@login_required
@exceptionHandler(logger, "can't access to user setting")
def setting():
    """

    用户设置个人信息

    """
    pass


@user.route('/manage')
@login_required
@exceptionHandler(logger, "can't access to user manage articles")
def manage():
    """

    用户管理文章

    """
    pass
