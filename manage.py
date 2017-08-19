from flask_script import Manager, Shell, Command
from app import db, createApp
from app.models import (ArticleTag, Article, OriginalArticleFormatType,
                        Reply, Review, Role, Tag, User, Following)


app = createApp()
manager = Manager(app)


def __makeShellContext():
    return dict(ArticleTag=ArticleTag, Article=Article,
                OriginalArticleFormatType=OriginalArticleFormatType,
                Following=Following, db=db, app=app,
                Reply=Reply, Review=Review, Role=Role, Tag=Tag, User=User)


manager.add_command('shell', Shell(make_context=__makeShellContext))


class InitDatabaseCommand(Command):
    """

    initialize database.

    """
    def run(self):
        Role.insertRoles()


manager.add_command('initDatabase', InitDatabaseCommand())


if __name__ == '__main__':
    manager.run()
