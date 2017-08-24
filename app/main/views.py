from flask import (render_template, Blueprint, current_app, request, abort)
from flask_login import login_required, current_user
from sqlalchemy import desc
from .logger import logger
from ..models import Article, Tag
from ..utility import exceptionHandler


main = Blueprint('main', __name__, template_folder="templates")


@main.route('/')
@exceptionHandler(logger, 'failed to visit homepage')
def index():
    pageNoStr = request.args.get('pageNo')
    pageNo = int(pageNoStr) if pageNoStr else 1
    pagination = (Article.query.order_by(desc(Article.creationDate)).
                  paginate(pageNo,
                           current_app.config['ARTICLE_COUNT_PER_PAGE'],
                           False))
    return render_template('main/index.html', pagination=pagination,
                           hotTags=Tag.
                           getHotTags(current_app.config['HOT_TAG_COUNT']))


@main.route('/subscriptions')
@login_required
@exceptionHandler(logger, "failed to get subscriptions")
def subscriptions():
    # subscription 订阅
    pageNo = request.args.get('pageNo') or 1
    pageNo = int(pageNo)
    followedUserIds = [record.userId for record in
                       current_user.followedRecords.all()]
    pagination = None
    if followedUserIds:
        pagination = Article.query.\
                     filter(Article.userId.in_(followedUserIds)).\
                     order_by(desc(Article.creationDate)).\
                     paginate(pageNo,
                              current_app.config['ARTICLE_COUNT_PER_PAGE'],
                              False)
    return render_template('main/subscriptions.html',
                           followedCount=len(followedUserIds),
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
    pagination = (Article.query.join(stmt, stmt.c.articleId == Article.id).
                  order_by(desc(Article.creationDate)).
                  paginate(pageNo,
                           current_app.config['ARTICLE_COUNT_PER_PAGE']))

    return render_template('main/concernedTags.html', currentTagId=tagId,
                           concernedTags=concernedTags, pagination=pagination)


@main.route('/showTag/<int:tagId>')
@exceptionHandler(logger, 'failed to show tag')
def showTag(tagId):
    tag = Tag.query.get_or_404(tagId)
    pageNo = int(request.args.get('pageNo') or 1)
    hot = request.args.get('hot')
    order = desc(Article.viewedCount) if hot else desc(Article.creationDate)

    stmt = tag.articles.subquery()
    pagination = (Article.query.join(stmt, Article.id == stmt.c.id).
                  order_by(order).
                  paginate(pageNo, current_app.config['ARTICLE_COUNT_PER_PAGE']))

    return render_template('main/showTag.html', tag=tag, pagination=pagination)
