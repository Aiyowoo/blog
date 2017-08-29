from os import path
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user 
from sqlalchemy import func, desc
from .logger import logger
from ..utility import exceptionHandler
from ..models import db, User, Tag, Article, ArticleTag


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
                  join(stmt, Tag.id == stmt.c.tagId).all())

    tagIdStr = request.args.get('tagId')
    if tagIdStr:
        try:
            tagId = int(tagIdStr)
        except:
            abort(400)
        if tagId not in (tag.id for tag, _ in tagRecords):
            abort(400)
        pagination = (user.articles.filter(Article.tagId == tagId).
                      paginate(pageNo, current_app.config['ARTICLE_COUNT_PER_PAGE']),
                      False)
    else:
        tagId = None
        pagination = (user.articles.
                     paginate(pageNo, current_app.config['ARTICLE_COUNT_PER_PAGE'], False))

    return render_template('user/home.html', user=user,
                           totalArticleCount = user.articles.count(),
                           pagination=pagination, tagId=tagId, join=path.join,
                           current_app=current_app, tagRecords=tagRecords)


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
