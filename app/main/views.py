from flask import (render_template, Blueprint, current_app, request)
from flask_login import login_required, current_user
from .logger import logger
from ..models import Article, Tag
from ..utility import exceptionHandler


main = Blueprint('main', __name__, template_folder="templates")


@main.route('/')
@exceptionHandler(logger, 'failed to visit homepage')
def index():
    pageNoStr = request.args.get('pageNo')
    pageNo = int(pageNoStr) if pageNoStr else 1
    pagination = (Article.query.order_by(Article.creationDate).
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
                     order_by(Article.creationDate).\
                     paginate(pageNo,
                              current_app.config['ARTICLE_COUNT_PER_PAGE'],
                              False)
    return render_template('main/subscriptions.html',
                           followedCount=len(followedUserIds),
                           pagination=pagination)
