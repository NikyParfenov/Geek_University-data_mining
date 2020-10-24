from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
)

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    header = Column(String, unique=True, nullable=False)
    post_date = Column(DateTime, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='posts')
    tag = relationship('Tag', secondary=tag_post, back_populates='posts')
    comments = relationship('Comment')


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post')
    comments = relationship('Comment')


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary=tag_post)


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(String, unique=False, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    post_id = Column(Integer, ForeignKey('post.id'))
    posts = relationship('Post', back_populates='comments')
    writer = relationship('Writer', back_populates='comments')
