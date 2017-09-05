# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 09:14:59 2017

@author: ivan
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import enum


class CollectionType(enum.Enum):
    rank = 1
    filtered = 2
    selection = 3
    raw = 4


engine = create_engine('sqlite:////home/ivan/flask/flaskTEC/tecrank/test.db')
Base = declarative_base()


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(200))
    parent = relationship('Collection', back_populates='sons')
    collectiontype = Column(Integer)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Name %r>' % self.name

    def as_dict(self):
        return {'id': self.id, 'name': self.name}


Collection.sons = relationship(
    "Collection", order_by=Collection.id, back_populates="collection")


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collections.id'))
    collection = relationship("Collection", back_populates="documents")
    title = Column(String(80), unique=True)
    contents = Column(String(1000))
    length = Column(Integer)

    def __init__(self, pcollection, ptitle, pcontent):
        self.collection = pcollection
        self.title = ptitle
        self.contents = pcontent

    def __repr__(self):
        return '<Title %r>' % self.title

    def as_dict(self):
        return {'id': self.id, 'title': self.title, 'contents': self.contents}


Collection.documents = relationship(
    "Document", order_by=Document.id, back_populates="collection")


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    atoken = Column(String(40), unique=True)
    length = Column(Integer)

    def __init__(self, atoken):
        self.atoken = atoken
        self.length = len(atoken)

    def __repr__(self):
        return '<Word %r>' % self.atoken


class WordOccurrence(Base):
    __tablename__ = 'word_occurrences'
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'))
    document_id = Column(Integer, ForeignKey('documents.id'))
    position = Column(Integer)

    def __init__(self, word_id, document_id, position):
        self.word_id = word_id
        self.document_id = document_id
        self.position = position

    def __repr__(self):
        return '<id %r>' % str(self.id)

# Document.words = relationship(
#    "WordOccurrence", order_by=WordOccurrence.id, back_populates="document")

# Word.documents = relationship(
#    "WordOccurrence", order_by=WordOccurrence.id, back_populates="word")
