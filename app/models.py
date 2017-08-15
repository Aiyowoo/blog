# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


Base = declarative_base()
metadata = Base.metadata


class ArticleTag(Base):
    __tablename__ = 'ArticleTags'

    articleId = Column(ForeignKey('Articles.id'), primary_key=True, nullable=False)
    tagId = Column(ForeignKey('Tags.id'), primary_key=True, nullable=False, index=True)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    Article = relationship('Article')
    Tag = relationship('Tag')


class Article(Base):
    __tablename__ = 'Articles'

    id = Column(Integer, primary_key=True)
    userId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    userName = Column(String(255), nullable=False)
    userProfilePicture = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    originalType = Column(ForeignKey('OriginalArticleFormatType.id'), nullable=False, index=True)
    originalSummary = Column(String(1), nullable=False)
    originalContent = Column(Text, nullable=False)
    firstContentPicture = Column(String(255))
    summary = Column(String(1), nullable=False)
    content = Column(Text, nullable=False)
    creationDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    lastModifiedDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    likeCount = Column(Integer, server_default=text("'0'"))
    dislikeCount = Column(Integer, server_default=text("'0'"))
    viewedCount = Column(Integer, server_default=text("'0'"))
    reviewCount = Column(Integer, server_default=text("'0'"))
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    OriginalArticleFormatType = relationship('OriginalArticleFormatType')
    User = relationship('User')


class OriginalArticleFormatType(Base):
    __tablename__ = 'OriginalArticleFormatType'

    id = Column(Integer, primary_key=True)
    name = Column(String(1), nullable=False)


class Reply(Base):
    __tablename__ = 'Replies'

    id = Column(Integer, primary_key=True)
    reviewId = Column(ForeignKey('Articles.id'), nullable=False, index=True)
    fromUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    fromUserName = Column(String(255), nullable=False)
    fromUserProfilePicture = Column(String(255), nullable=False)
    toUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    toUserName = Column(String(255), nullable=False)
    toUserProfilePicture = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    content = Column(Text, nullable=False)
    pid = Column(ForeignKey('Replies.id'), index=True)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    User = relationship('User', primaryjoin='Reply.fromUserId == User.id')
    parent = relationship('Reply', remote_side=[id])
    Article = relationship('Article')
    User1 = relationship('User', primaryjoin='Reply.toUserId == User.id')


class Review(Base):
    __tablename__ = 'Reviews'

    id = Column(Integer, primary_key=True)
    userId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    userName = Column(String(255), nullable=False)
    userProfilePicture = Column(String(255), nullable=False)
    articleId = Column(ForeignKey('Articles.id'), nullable=False, index=True)
    creationDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    content = Column(Text, nullable=False)
    deleted = Column(Integer, nullable=False, server_default=text("'0'"))

    Article = relationship('Article')
    User = relationship('User')


class Role(Base):
    __tablename__ = 'Roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    permissions = Column(Integer, nullable=False)


class Tag(Base):
    __tablename__ = 'Tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(1), nullable=False)
    createUserId = Column(ForeignKey('Users.id'), nullable=False, index=True)
    creationDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    User = relationship('User')


class User(UserMixin, Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    role = Column(ForeignKey('Roles.id'), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True)
    hashedPassword = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    creationDate = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    introduction = Column(String(255), nullable=False)
    profilePicture = Column(String(255))

    Role = relationship('Role')

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
