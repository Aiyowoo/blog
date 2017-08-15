from flask_script import Manager, Shell
from app import createApp, db
from app.models import (ArticleTag, Article, OriginalArticleFormatType,
                        Reply, Review, Role, Tag, User)


app = createApp()
manager = Manager(app)


def __makeShellContext():
    return dict(ArticleTag=ArticleTag, Artcle=Article,
                OriginalArticleFormatType=OriginalArticleFormatType,
                db=db,
                Reply=Reply, Review=Review, Role=Role, Tag=Tag, User=User)


manager.add_command('shell', Shell(make_context=__makeShellContext))


if __name__ == '__main__':
    manager.run()
