from flask import (redirect, url_for, flash, render_template,
                   Blueprint, current_app, request)
from flask_login import login_required, current_user
from .logger import logger
from ..models import Article
from ..utility import exceptionHandler


main = Blueprint('main', __name__, template_folder="templates")


@main.route('/')
@exceptionHandler(logger, 'failed to visit /look')
def index():
    return "hello world"


@main.route('/subscriptions')
@login_required
@exceptionHandler(logger, "failed to get followed users' articles")
def subscriptions():
    # subscription 订阅
    pageNo = request.args.get('pageNo') or 1
    pageNo = int(pageNo)
    followedUserIds = [record.userId for record in current_user.followedRecords.all()]
    pagination = None
    if followedUserIds:
        pagination = Article.query.filter(Article.userId.in_(followedUserIds)).\
                     order_by(Article.creationDate).\
                     paginate(pageNo, current_app.config['ARTICLE_COUNT_PER_PAGE'], False)
    return render_template('main/subscriptions.html', followedCount=len(followedUserIds),
                           pagination=pagination)


