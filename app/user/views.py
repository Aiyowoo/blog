from os import path
from flask import (Blueprint, render_template, redirect, url_for,
                   request, current_app, abort, flash)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from ..utility import exceptionHandler
from ..models import db, User, Tag, Article, ArticleTag
from .logger import logger
from .forms import BaseInfoForm, PasswordForm


user = Blueprint('user', __name__, template_folder='templates')


@user.route('/homepage/<int:userId>')
@exceptionHandler(logger, "can't access to user homepage")
def home(userId):
    """

    用户主页，是否登录均可访问

    """
    pageNoStr = request.args.get('pageNo')
    try:
        pageNo = int(pageNoStr) if pageNoStr else 1
    except:
        abort(400)

    user = User.query.get_or_404(userId)

    articleIds = db.session.query(Article.id).filter(Article.userId == user.id)
    stmt = (db.session.query(ArticleTag.tagId, func.count('*').
                             label('count')).
            filter(ArticleTag.articleId.in_(articleIds)).
            group_by(ArticleTag.tagId).subquery())
    tagRecords = (db.session.query(Tag, stmt.c.count).
                  join(stmt, Tag.id == stmt.c.tagId).
                  order_by(Tag.name).
                  all())

    tagIdStr = request.args.get('tagId')
    if tagIdStr:
        try:
            tagId = int(tagIdStr)
        except:
            abort(400)
        if tagId not in (tag.id for tag, _ in tagRecords):
            abort(400)
        pagination = (user.articles.filter(Article.tagId == tagId).
                      order_by(Article.creationDate).
                      paginate(pageNo,
                               current_app.config['ARTICLE_COUNT_PER_PAGE']),
                      False)
    else:
        tagId = None
        pagination = (user.articles.
                      order_by(Article.creationDate).
                      paginate(pageNo,
                               current_app.config['ARTICLE_COUNT_PER_PAGE'],
                               False))

    return render_template('user/home.html', user=user,
                           totalArticleCount=user.articles.count(),
                           pagination=pagination, tagId=tagId, join=path.join,
                           current_app=current_app, tagRecords=tagRecords)


@user.route('/setting')
@login_required
@exceptionHandler(logger, "can't access to user setting")
def setting():
    """

    用户设置个人信息

    """
    return redirect(url_for('.setBaseInfo'))


@user.route('/setBaseInfo', methods=['GET', 'POST'])
@login_required
@exceptionHandler(logger, "can't access to set base info")
def setBaseInfo():
    baseInfoForm = BaseInfoForm()
    if baseInfoForm.validate_on_submit():
        if baseInfoForm.profilePicture.data:
            imageFile = baseInfoForm.profilePicture.data
            uploadedFilename = secure_filename(imageFile.filename)
            filename = (path.
                        join('app/static',
                             current_app.
                             config['USER_PROFILE_PICTURE_SAVE_DIR'],
                             str(current_user.id)
                             + uploadedFilename[uploadedFilename.rfind('.'):]))
            imageFile.save(filename)
            current_user.profilePicture = filename
        if baseInfoForm.name.data:
            current_user.name = baseInfoForm.name.data
        if baseInfoForm.introduction.data:
            current_user.introduction = baseInfoForm.introduction.data
        db.session.add(current_user)
        db.session.commit()
        flash('修改成功')
    else:
        baseInfoForm.name.data = current_user.name
        baseInfoForm.introduction.data = current_user.introduction
    return render_template('user/setting.html', baseInfoForm=baseInfoForm)


@user.route('/setPassword', methods=['GET', 'POST'])
@login_required
@exceptionHandler(logger, "can't access to set password")
def setPassword():
    passwordForm = PasswordForm()
    if passwordForm.validate_on_submit():
        current_user.password = passwordForm.newPassword.data
        db.session.add(current_user)
        db.session.commit()
        flash('修改成功')
    return render_template('user/setting.html', passwordForm=passwordForm)


@user.route('/manage')
@login_required
@exceptionHandler(logger, "can't access to user manage articles")
def manage():
    """

    用户管理文章

    """
    pass
