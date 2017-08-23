from flask_script import Manager, Shell, Command
from app import db, createApp
from app.models import (ArticleTag, Article, OriginalArticleFormatType,
                        Reply, Review, Role, Tag, User, Following,
                        generateFakeRecords)
import log


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


class GenerateFakeRecordsCommand(Command):
    """

    生成测试用的虚假数据

    """
    def run(self):
        generateFakeRecords()


manager.add_command('initDatabase', InitDatabaseCommand())
manager.add_command('generateFakeRecords', GenerateFakeRecordsCommand())


if __name__ == '__main__':
    log.queueListener.start()
    manager.run()
    log.queueListener.stop()
