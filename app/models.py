# coding: utf-8
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from . import db, loginManager
from appInstance import app


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
    creationDate = db.Column(db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

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
    userProfilePicture = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    originalType = db.Column(db.ForeignKey('OriginalArticleFormatType.id'),
                          nullable=False, index=True)
    originalSummary = db.Column(db.String(1), nullable=False)
    originalContent = db.Column(db.Text, nullable=False)
    firstContentPicture = db.Column(db.String(255))
    summary = db.Column(db.String(1), nullable=False)
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
                              backref=db.backref('articles', lazy='dynamic'))
    user = db.relationship('User', uselist=False,
                        backref=db.backref('articles', lazy='dynamic'))

    def __repr__(self):
        return '<Article id={}, userId={}, userName={}, title={}>'.\
            format(self.id, self.userId, self.userName, self.title)


class OriginalArticleFormatType(db.Model):
    __tablename__ = 'OriginalArticleFormatType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), nullable=False)

    def __repr__(self):
        return '<OriginalArticleFormatType id={}, name={}>'.\
            format(self.id, self.name)


class Reply(db.Model):
    __tablename__ = 'Replies'

    id = db.Column(db.Integer, primary_key=True)
    reviewId = db.Column(db.ForeignKey('Reviews.id'), nullable=False, index=True)
    fromUserId = db.Column(db.ForeignKey('Users.id'), nullable=False, index=True)
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

    fromUser = db.relationship('User', primaryjoin='Reply.fromUserId == User.id')
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
    articleId = db.Column(db.ForeignKey('Articles.id'), nullable=False, index=True)
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
            'user': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES),
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
    name = db.Column(db.String(1), nullable=False)
    createUserId = db.Column(db.ForeignKey('Users.id'), nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))

    createUser = db.relationship('User')

    def __repr__(self):
        return '<Tag id={}, name={}, creationDate={}>'.\
            format(self.id, self.name, self.creationDate)


class Following(db.Model):
    __tablename__ = 'Following'

    userId = db.Column(db.ForeignKey('Users.id'), primary_key=True, nullable=False)
    followerId = db.Column(db.ForeignKey('Users.id'), primary_key=True, nullable=False, index=True)
    creationDate = db.Column(db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    followedUser = db.relationship('User', primaryjoin='Following.userId == User.id',
                                   backref=db.backref('followedRecords'), uselist=False)
    follower = db.relationship('User', primaryjoin='Following.followerId == User.id',
                               backref=db.backref('followerRecords'), uselist=False)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    roleId = db.Column(db.ForeignKey('Roles.id'), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashedPassword = db.Column(db.String(64), nullable=False)
    confirmed = db.Column(db.Integer, nullable=False, server_default=text("'0'"))
    name = db.Column(db.String(255), nullable=False)
    creationDate = db.Column(db.DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP ON \
                          UPDATE CURRENT_TIMESTAMP"))
    introduction = db.Column(db.String(255), nullable=False)
    profilePicture = db.Column(db.String(255))

    role = db.relationship('Role', uselist=False, backref=db.backref('users', lazy='dynamic'))

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
        serializer = Serializer(app.config['CONFIRM_TOKEN_SECRET_KEY'],
                                expires_in=3600)
        return serializer.dumps({'confirmedUserId', self.id})

    def confirm(self, token):
        '''

        token正确，完成用户邮箱验证，返回True
        否则返回False

        '''
        assert not self.confirmed, '{} has confirmed!'.format(str(self))
        serializer = Serializer(app.config['CONFIRM_TOKEN_SECRET_KEY'],
                                expires_in=3600)
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        if data.get('confirmUserId') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permission):
        return self.role.permissions & permission


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False


# Role.USER_ID = Role.query.filter_by(name='user').first().id
# Role.ADMIN_ID = Role.query.filter_by(name='amdin').first().id

loginManager.anonymous_user = AnonymousUser


@loginManager.user_loader
def loadUser(userId):
    return User.get(userId)
