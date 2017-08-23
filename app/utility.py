from functools import wraps
from flask import abort
from .models import db


def exceptionHandler(logger, info):
    def wrapper(func):
        @wraps(func)
        def handler(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                logger.exception(info)
                db.session.rollback()
                raise
        return handler
    return wrapper
