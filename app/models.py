# coding: utf-8
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func, desc, Table
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired


db = SQLAlchemy()


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MANAGE_COMMENTS = 0x08
    ADMIN = 0x80


# 对于sqlacodegen生成的代码如果想使用flask-sqlalchemy应改为继承自db.Model
class ArticleTag(db.Model):
    __tablename__ = 'ArticleTags'

    articleId = db.Column(db.ForeignKey('Articles.id'),
                          primary_key=True, nullable=False)
    tagId = db.Column(db.ForeignKey('Tags.id'), primary_key=True,
                      nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))

    article = db.relationship('Article', uselist=False,
                              backref=db.backref('tagRecords', lazy='dynamic'))
    tag = db.relationship('Tag', uselist=False,
                          backref=db.backref('articleRecords', lazy='dynamic'))

    def __repr__(self):
        return '<ArticleTag articleId={}, tagId={}, deleted={}>'.\
            format(self.articleId, self.tagId, self.creationDate)


class Article(db.Model):
    __tablename__ = 'Articles'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.ForeignKey('Users.id'), nullable=False, index=True)
    userName = db.Column(db.String(255), nullable=False)
    userProfilePicture = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    originalTypeId = db.Column(db.ForeignKey('OriginalArticleFormatType.id'),
                               nullable=False, index=True)
    originalSummary = db.Column(db.String(2048), nullable=False)
    originalContent = db.Column(db.Text, nullable=False)
    firstContentPicture = db.Column(db.String(255))
    summary = db.Column(db.String(2048), nullable=False)
    content = db.Column(db.Text, nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))
    lastModifiedDate = db.Column(db.DateTime, nullable=False,
                                 server_default=text("CURRENT_TIMESTAMP"))
    likeCount = db.Column(db.Integer, server_default=text("'0'"))
    dislikeCount = db.Column(db.Integer, server_default=text("'0'"))
    viewedCount = db.Column(db.Integer, server_default=text("'0'"))
    reviewCount = db.Column(db.Integer, server_default=text("'0'"))
    deleted = db.Column(db.Integer, nullable=False, server_default=text("'0'"))

    formatType = db.relationship('OriginalArticleFormatType', uselist=False,
                                 backref=db.backref('articles',
                                                    lazy='dynamic'))
    user = db.relationship('User', uselist=False,
                           backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return '<Article id={}, userId={}, userName={}, title={}>'.\
            format(self.id, self.userId, self.userName, self.title)


class OriginalArticleFormatType(db.Model):
    __tablename__ = 'OriginalArticleFormatType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<OriginalArticleFormatType id={}, name={}>'.\
            format(self.id, self.name)


class Reply(db.Model):
    __tablename__ = 'Replies'

    id = db.Column(db.Integer, primary_key=True)
    reviewId = db.Column(db.ForeignKey('Reviews.id'),
                         nullable=False, index=True)
    fromUserId = db.Column(db.ForeignKey('Users.id'),
                           nullable=False, index=True)
    fromUserName = db.Column(db.String(255), nullable=False)
    fromUserProfilePicture = db.Column(db.String(255), nullable=False)
    toUserId = db.Column(db.ForeignKey('Users.id'), nullable=False, index=True)
    toUserName = db.Column(db.String(255), nullable=False)
    toUserProfilePicture = db.Column(db.String(255), nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))
    content = db.Column(db.Text, nullable=False)
    pid = db.Column(db.ForeignKey('Replies.id'), index=True)
    deleted = db.Column(db.Integer, nullable=False, server_default=text("'0'"))

    fromUser = db.relationship('User',
                               primaryjoin='Reply.fromUserId == User.id')
    parent = db.relationship('Reply', remote_side=[id])
    review = db.relationship('Review', uselist=False,
                             backref=db.backref('replies', lazy='dynamic'))
    toUser = db.relationship('User', primaryjoin='Reply.toUserId == User.id')

    def __repr__(self):
        return '<Reply id={}, fromUserId={}, fromUserName={}, \
        toUserId={}, toUserName={}>'.format(self.id, self.fromUserId,
                                            self.fromUserName, self.toUserId,
                                            self.toUsername)


class Review(db.Model):
    __tablename__ = 'Reviews'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.ForeignKey('Users.id'), nullable=False, index=True)
    userName = db.Column(db.String(255), nullable=False)
    userProfilePicture = db.Column(db.String(255), nullable=False)
    articleId = db.Column(db.ForeignKey('Articles.id'),
                          nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))
    content = db.Column(db.Text, nullable=False)
    deleted = db.Column(db.Integer, nullable=False, server_default=text("'0'"))

    article = db.relationship('Article', uselist=False,
                              backref=db.backref('reviews', lazy='dynamic'))
    user = db.relationship('User', uselist=False,
                           backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        summary = self.content[:20] + '' if len(self.content) > 20 else "..."
        return '<Review id={}, userName={}, articleId={}, content={}>'.\
            format(self.id, self.userName, self.articleId, summary)


class Role(db.Model):
    __tablename__ = 'Roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.Integer, nullable=False)

    USER_ID = 1
    ADMIN_ID = 2

    @staticmethod
    def insertRoles():
        roles = {
            'user': (Permission.FOLLOW | Permission.COMMENT |
                     Permission.WRITE_ARTICLES),
            'admin': (Permission.ADMIN)
        }
        for name, permissions in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name)
                role.permissions = permissions
                db.session.add(role)
                db.session.commit()

    def __repr__(self):
        return '<Role id={}, name={}, permissions={}>'.\
            format(self.id, self.name,
                   '0x' + hex(self.permissions or 0)[2:].zfill(8))


class Tag(db.Model):
    __tablename__ = 'Tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    createUserId = db.Column(db.ForeignKey('Users.id'),
                             nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))

    createUser = db.relationship('User')

    def __repr__(self):
        return '<Tag id={}, name={}, creationDate={}>'.\
            format(self.id, self.name, self.creationDate)

    @staticmethod
    def getHotTagRecords(count):
        """

        获取前count个比较热门的主题，该主题下文章数量（排除已删除的）

        """
        invalidArticleIds = (db.session.query(Article.id).
                             filter(Article.deleted == True))
        # stmt = (db.session.query(ArticleTag.tagId,
        #                          func.count('*').label('count')).
        #         join(invalidArticleIds,
        #              ArticleTag.articleId == invalidArticleIds.c.id).
        #         group_by(ArticleTag.tagId).
        #         order_by(desc(func.count('*'))).limit(count).subquery())
        stmt = (db.session.query(ArticleTag.tagId,
                                 func.count('*').label('count')).
                filter(ArticleTag.articleId.notin_(invalidArticleIds)).
                group_by(ArticleTag.tagId).
                order_by(desc(func.count('*'))).limit(count).subquery())
        return (db.session.query(Tag, stmt.c.count).
                join(stmt, Tag.id == stmt.c.tagId).
                order_by(desc(stmt.c.count)).all())


t_CencernedTags = Table(
    'ConcernedTags', db.Model.metadata,
    db.Column('userId', db.ForeignKey('Users.id'),
              primary_key=True, nullable=False),
    db.Column('tagId', db.ForeignKey('Tags.id'),
              primary_key=True, nullable=False, index=True)
)


class Following(db.Model):
    __tablename__ = 'Following'

    userId = db.Column(db.ForeignKey('Users.id'),
                       primary_key=True, nullable=False)
    followerId = db.Column(db.ForeignKey('Users.id'), primary_key=True,
                           nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))

    followedUser = db.relationship('User',
                                   primaryjoin='Following.userId == User.id',
                                   backref=db.backref('followerRecords',
                                                      lazy='dynamic'),
                                   uselist=False)
    follower = db.relationship('User',
                               primaryjoin='Following.followerId == User.id',
                               backref=db.backref('followedRecords',
                                                  lazy='dynamic'),
                               uselist=False)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    roleId = db.Column(db.ForeignKey('Roles.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashedPassword = db.Column(db.String(64), nullable=False)
    confirmed = db.Column(db.Integer, nullable=False,
                          server_default=text("'0'"))
    name = db.Column(db.String(255), nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False,
                             server_default=text("CURRENT_TIMESTAMP ON \
                          UPDATE CURRENT_TIMESTAMP"))
    introduction = db.Column(db.String(255), nullable=False)
    profilePicture = db.Column(db.String(255))

    role = db.relationship('Role', uselist=False,
                           backref=db.backref('users', lazy='dynamic'))
    concernedTags = db.relationship('Tag', secondary=t_CencernedTags,
                                    lazy='dynamic',
                                    backref=db.backref('followers',
                                                       lazy='dynamic'))

    @staticmethod
    def createAUser(*args, **kwargs):
        """

        创建一个角色为User的用户，并不存入数据库

        """
        user = User(*args, **kwargs)
        user.roleId = Role.USER_ID
        return user

    @staticmethod
    def createAnAdmin(*args, **kwargs):
        """

        创建并返回一个admin类型的用户，并不存入数据库

        """
        admin = User(*args, **kwargs)
        admin.roleId = Role.ADMIN_ID
        return admin

    def __repr__(self):
        return '<User email={}, name={}>'.format(self.email, self.name)

    @property
    def password(self):
        raise AttributeError('Unable to read password!')

    @password.setter
    def password(self, newPassword):
        """

        传入未加密的密码，赋值为加密后的密码

        """
        self.hashedPassword = generate_password_hash(newPassword)

    def checkPassword(self, password):
        """

        检查密码是否正确

        """
        return check_password_hash(self.hashedPassword, password)

    def generateConfirmToken(self):
        serializer = Serializer(current_app.config['CONFIRM_TOKEN_SECRET_KEY'],
                                expires_in=3600)
        return serializer.dumps({'confirmedUserId': self.id})

    def confirm(self, token):
        '''

        token正确，完成用户邮箱验证，返回True
        否则返回False

        '''
        assert not self.confirmed, '{} has confirmed!'.format(str(self))
        serializer = Serializer(current_app.config['CONFIRM_TOKEN_SECRET_KEY'],
                                expires_in=3600)
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        if data.get('confirmedUserId') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permission):
        return self.role.permissions & permission

    def getFollowedArticleCount(self):
        stmt = (db.session.query(Following.userId).
                filter(Following.followerId == self.id)).subquery()
        return (db.session.query(Article).
                join(stmt, Article.userId == stmt.c.userId).count())


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False


# Role.USER_ID = Role.query.filter_by(name='user').first().id
# Role.ADMIN_ID = Role.query.filter_by(name='amdin').first().id


def __generateFakeUsers(count):
    import forgery_py
    existedEmail = set(user.email for user in User.query.all())
    for i in range(count):
        email = forgery_py.internet.email_address()
        if email not in existedEmail:
            name = forgery_py.name.last_name()
            user = User.createAUser(email=email, name=name)
            user.password = 'wyljaaaa'
            user.confirmed = True
            db.session.add(user)
            existedEmail.add(email)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def __generateFakeTags(count):
    import forgery_py
    from random import randint
    userCount = User.query.count()
    assert userCount, 'There is no user!'
    existedTagnames = set(tag.name for tag in Tag.query.all())
    for i in range(count):
        tagname = forgery_py.name.industry()
        if tagname not in existedTagnames:
            newTag = Tag(name=tagname,
                         createUserId=randint(1, userCount - 1),
                         creationDate=forgery_py.date.date(True))
            db.session.add(newTag)
            existedTagnames.add(tagname)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def __generateFakeConcernedRecords(count):
    from random import choice
    existed = set()
    users = User.query.all()
    tags = Tag.query.all()
    for i in range(count):
        user = choice(users)
        tag = choice(tags)
        if (user.id, tag.id) not in existed:
            user.concernedTags.append(tag)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def __generateFakeArticles(count):
    import forgery_py
    from random import randint
    userCount = User.query.count()
    assert userCount, 'There is no user!'
    for i in range(count):
        user = User.query.offset(randint(0, userCount - 1)).first()
        article = Article()
        article.userId = user.id
        article.userName = user.name
        article.title = forgery_py.lorem_ipsum.title()
        article.originalTypeId = 1
        article.summary = forgery_py.lorem_ipsum.sentences(randint(10, 20))
        article.content = ''
        article.originalSummary = ''
        article.originalContent = ''
        article.lastModifiedDate = forgery_py.date.date(True)

        db.session.add(article)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def __generateFakeArticleTags():
    from random import randint, choice
    articles = Article.query.all()
    tags = Tag.query.all()
    for article in articles:
        attachedTags = set()
        for i in range(randint(0, 3)):
            attachedTags.add(choice(tags))
        for tag in attachedTags:
            record = ArticleTag()
            record.article = article
            record.tag = tag
            db.session.add(record)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def __generateFakeFollowings(count):
    from random import choice
    userIds = [user.id for user in User.query.all()]
    existedFollowings = set((following.userId, following.followerId)
                            for following in Following.query.all())
    for i in range(count):
        userId = choice(userIds)
        followerId = choice(userIds)
        if userId != followerId and \
           (userId, followerId) not in existedFollowings:
            following = Following(userId=userId, followerId=followerId)
            db.session.add(following)
            existedFollowings.add((userId, followerId))

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def generateFakeRecords():
    __generateFakeUsers(10)
    __generateFakeTags(100)
    __generateFakeConcernedRecords(100)
    __generateFakeArticles(1000)
    __generateFakeArticleTags()
    __generateFakeFollowings(20)
