from flask import (render_template, Blueprint, current_app, request, abort)
from flask_login import login_required, current_user
from sqlalchemy import desc, func, and_
from .logger import logger
from ..models import Article, Tag, ArticleTag, db, User, Following
from ..utility import exceptionHandler


main = Blueprint('main', __name__, template_folder="templates")


@main.route('/')
@exceptionHandler(logger, 'failed to visit homepage')
def index():
    pageNoStr = request.args.get('pageNo')
    pageNo = int(pageNoStr) if pageNoStr else 1
    pagination = (Article.query.filter(Article.deleted == False).
                  order_by(desc(Article.creationDate)).
                  paginate(pageNo,
                           current_app.config['ARTICLE_COUNT_PER_PAGE'],
                           False))
    return render_template('main/index.html', pagination=pagination,
                           hotTagRecords=Tag.
                           getHotTagRecords(current_app.config['HOT_TAG_COUNT']))


@main.route('/subscriptions')
@login_required
@exceptionHandler(logger, "failed to get subscriptions")
def subscriptions():
    # subscription 订阅
    try:
        pageNo = int(request.args.get('pageNo') or 1)
    except:
        abort(400)

    followedUserIdsQuery = (db.session.query(Following.userId).
                            filter(Following.followerId == current_user.id))
    followedCount = followedUserIdsQuery.count()

    pagination = None
    if followedCount:
        pagination = (db.session.query(Article).
                      filter(and_(Article.deleted == False,
                                  Article.userId.in_(followedUserIdsQuery))).
                      order_by(desc(Article.creationDate)).
                      paginate(pageNo,
                               current_app.config['ARTICLE_COUNT_PER_PAGE'],
                               False))
    return render_template('main/subscriptions.html',
                           followedCount=followedCount,
                           pagination=pagination)


@main.route('/concernedTags')
@login_required
@exceptionHandler(logger, 'failed to visit /concernedTags')
def concernedTags():
    concernedTags = current_user.concernedTags.all()
    if concernedTags:
        try:
            tagId = int(request.args.get('tagId') or concernedTags[0].id)
            pageNo = int(request.args.get('pageNo') or 1)
            if tagId not in (tag.id for tag in concernedTags):
                raise ValueError("{} didn't concerned tag {}".
                                 format(current_user, tagId))
        except:
            abort(400)

    stmt = Tag.query.get(tagId).articleRecords.subquery()
    pagination = (Article.query.filter(Article.deleted == False).
                  join(stmt, stmt.c.articleId == Article.id).
                  order_by(desc(Article.creationDate)).
                  paginate(pageNo,
                           current_app.config['ARTICLE_COUNT_PER_PAGE'],
                           False))

    return render_template('main/concernedTags.html', currentTagId=tagId,
                           concernedTags=concernedTags, pagination=pagination)


@main.route('/showTag/<int:tagId>')
@exceptionHandler(logger, 'failed to show tag')
def showTag(tagId):
    tag = Tag.query.get_or_404(tagId)
    try:
        pageNo = int(request.args.get('pageNo') or 1)
    except:
        abort(400)

    order = (desc(Article.viewedCount) if request.args.get('hot')
             else desc(Article.creationDate))

    articleIdsQuery = (db.session.query(ArticleTag.articleId).
                       filter(ArticleTag.tagId == tag.id).subquery())
    pagination = (Article.query.filter(Article.deleted == False).
                  join(stmt, Article.id == articleIdsQuery.c.articleId).
                  order_by(order).order_by(desc(Article.creationDate)).
                  paginate(pageNo, current_app.config['ARTICLE_COUNT_PER_PAGE']))

    stmt = db.session.query(ArticleTag.articleId).filter(ArticleTag.tagId == tag.id).subquery()
    stmt2 = (db.session.query(Article.userId, func.count(Article.id).label('count')).
             filter(Article.deleted == False).
             join(stmt, stmt.c.articleId == Article.id).
             group_by(Article.userId).order_by(desc(func.count(Article.id))).
             limit(current_app.config['FAMOUS_USER_COUNT'])).subquery()
    famousUserRecords = (db.session.query(User, stmt2.c.count).
                         join(stmt2, User.id == stmt2.c.userId).
                         order_by(desc(stmt2.c.count)).all())

    return render_template('main/showTag.html', tag=tag,
                           pagination=pagination,
                           famousUserRecords=famousUserRecords)
