from flask import (redirect, url_for, flash, render_template, Blueprint)


main = Blueprint('main', __name__, template_folder="templates")


@main.route('/')
def index():
    pass
