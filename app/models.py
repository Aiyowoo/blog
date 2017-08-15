# coding: utf-8
from sqlalchemy import (Column, DateTime, ForeignKey,
                        Integer, String, Text, text)
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db


# 对于sqlacodegen生成的代码如果想使用flask-sqlalchemy应改为继承自db.Model
class ArticleTag(db.Model):
    __tablename__ = 'ArticleTags'

    articleId = Column(ForeignKey('Articles.id'),
                       primary_key=True, nullable=False)
    tagId = Column(ForeignKey('Tags.id'), primary_key=True,
                   nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    Article = relationship('Article')
    Tag = relationship('Tag')

    def __repr__(self):
        return '<ArticleTag articleId={}, tagId={}, deleted={}>'.\
            format(self.articleId, self.tagId, self.deleted)


class Article(db.Model):
    __tablename__ = 'Articles'

    id = Column(Integer, primary_key=True)
    userId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    userName = Column(String(255), nullable=False)
    userProfilePicture = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    originalType = Column(ForeignKey('OriginalArticleFormatType.id'),
                          nullable=False, index=True)
    originalSummary = Column(String(1), nullable=False)
    originalContent = Column(Text, nullable=False)
    firstContentPicture = Column(String(255))
    summary = Column(String(1), nullable=False)
    content = Column(Text, nullable=False)
    creationDate = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    lastModifiedDate = Column(DateTime, nullable=False,
                              server_default=text("CURRENT_TIMESTAMP"))
    likeCount = Column(Integer, server_default=text("'0'"))
    dislikeCount = Column(Integer, server_default=text("'0'"))
    viewedCount = Column(Integer, server_default=text("'0'"))
    reviewCount = Column(Integer, server_default=text("'0'"))
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    OriginalArticleFormatType = relationship('OriginalArticleFormatType')
    User = relationship('User')

    def __repr__(self):
        return '<Article id={}, userId={}, userName={}, title={}>'.\
            format(self.id, self.userId, self.userName, self.title)


class OriginalArticleFormatType(db.Model):
    __tablename__ = 'OriginalArticleFormatType'

    id = Column(Integer, primary_key=True)
    name = Column(String(1), nullable=False)

    def __repr__(self):
        return '<OriginalArticleFormatType id={}, name={}>'.\
            format(self.id, self.name)


class Reply(db.Model):
    __tablename__ = 'Replies'

    id = Column(Integer, primary_key=True)
    reviewId = Column(ForeignKey('Articles.id'), nullable=False, index=True)
    fromUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    fromUserName = Column(String(255), nullable=False)
    fromUserProfilePicture = Column(String(255), nullable=False)
    toUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    toUserName = Column(String(255), nullable=False)
    toUserProfilePicture = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    content = Column(Text, nullable=False)
    pid = Column(ForeignKey('Replies.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    User = relationship('User', primaryjoin='Reply.fromUserId == User.id')
    parent = relationship('Reply', remote_side=[id])
    Article = relationship('Article')
    User1 = relationship('User', primaryjoin='Reply.toUserId == User.id')

    def __repr__(self):
        return '<Reply id={}, fromUserId={}, fromUserName={}, \
        toUserId={}, toUserName={}>'.format(self.id, self.fromUserId,
                                            self.fromUserName, self.toUserId,
                                            self.toUsername)


class Review(db.Model):
    __tablename__ = 'Reviews'

    id = Column(Integer, primary_key=True)
    userId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    userName = Column(String(255), nullable=False)
    userProfilePicture = Column(String(255), nullable=False)
    articleId = Column(ForeignKey('Articles.id'), nullable=False, index=True)
    creationDate = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    content = Column(Text, nullable=False)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    Article = relationship('Article')
    User = relationship('User')

    def __repr__(self):
        summary = self.content[:20] + '' if len(self.content) > 20 else "..."
        return '<Review id={}, userName={}, articleId={}, content={}>'.\
            format(self.id, self.userName, self.articleId, summary)


class Role(db.Model):
    __tablename__ = 'Roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    permissions = Column(Integer, nullable=False)

    def __repr__(self):
        return '<Role id={}, name={}, permissions={}>'.\
            format(self.id, self.name,
                   '0x' + hex(self.permissions)[2:].zfill(8))


class Tag(db.Model):
    __tablename__ = 'Tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(1), nullable=False)
    createUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    creationDate = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))

    User = relationship('User')

    def __repr__(self):
        return '<Tag id={}, name={}, creationDate={}>'.\
            format(self.id, self.name, self.creationDate)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    role = Column(ForeignKey('Roles.id'), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True)
    hashedPassword = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP ON \
                          UPDATE CURRENT_TIMESTAMP"))
    introduction = Column(String(255), nullable=False)
    profilePicture = Column(String(255))

    Role = relationship('Role')

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
