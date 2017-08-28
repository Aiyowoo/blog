from flask import Blueprint
from flask_login import login_required, current_user
from .logger import logger
from ..utility import exceptionHandler


article = Blueprint('article', __name__, template_folder='templates')


@article.route('/article/<int:articleId>')
@exceptionHandler(logger, "can't show article")
def showArticle(articleId):
    pass


@article.route('/addArticle')
@login_required
@exceptionHandler(logger, "can't add a new article")
def addArticle():
    pass


@article.route('/removeArticle/<int:articleId>')
@login_required
@exceptionHandler(logger, "can't remove article")
def removeArticle(articleId):
    pass


@article.route('/changeArticle/<int:articleId>')
@login_required
@exceptionHandler(logger, "can't change article")
def changeArticle(articleId):
    pass


@article.route('/addReview/<int:articleId>')
@login_required
@exceptionHandler(logger, "can't add a review")
def addReview(articleId):
    pass


@article.route('/removeReview/<int:reviewId>')
@login_required
@exceptionHandler(logger, "can't remove a review")
def removeReview(reviewId):
    pass
