# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 09:14:59 2017

@author: ivan
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ivan/flask/flaskTEC/tecrank/test.db'
db = SQLAlchemy(app)


class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '<Name %r>' % self.name

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
    collection = db.relationship("Collection", back_populates="documents")
    title = db.Column(db.String(80), unique=True)
    contents = db.Column(db.String(1000))

    def __init__(self, pcollection, ptitle, pcontent):
        self.collection = pcollection
        self.title = ptitle
        self.contents = pcontent
        
    def __repr__(self):
        return '<Title %r>' % self.title

Collection.documents = db.relationship(
        "Document", order_by=Document.id, back_populates="collection")

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(40))
    def __init__(self, content):
        self.content = content
    def __repr__(self):
        return '<Word-id %r>' % self.word, self.id
    
class WordOccurrence(db.Model):
    __tablename__ = 'word_occurrences'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    position =  db.Column(db.Integer)
    def __init__(self, word_id, document_id, position):
        self.word_id = word_id
        self.document_id = document_id
        self.position = position
    def __repr__(self):
        return '<Word-id %r>' % self.content, self.id