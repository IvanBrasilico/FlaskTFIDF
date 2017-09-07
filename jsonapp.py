#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 18:28:17 2017

@author: IvanBrasilico
"""
from flask import jsonify, request, Flask
from sqlalchemy.orm import sessionmaker
from models.models import Collection, Word, Document
from models.models import engine
import utils.spelling_corrector as spell
from models.collectionmanager import CollectionManager
from flask_cors import CORS

if __name__ == '__main__':
    app = Flask(__name__, static_url_path='/static')
    CORS(app)
else:
    from webapp import app

Session = sessionmaker(bind=engine)
session = Session()
selected_collection_id = 1


@app.route('/_test')
def test():
    return jsonify([{"title": "1", "contents": "TESTE 1"},
                    {"title": "2", "contents": "TESTE 2"}])


@app.route('/_rank')
def rank():
    """Get words, return ranked results"""
    words = request.args.get('words', 0, type=str)
    result = []
    if words and isinstance(words, str):
        collection = session.query(Collection).filter_by(
                                               id=selected_collection_id).one()
        manager = CollectionManager(session, collection)
        result = manager.bm25(words)
    return jsonify(result)


@app.route('/_correct')
def correct():
    """Get words, return ranked results"""
    words = request.args.get('words', 0, type=str)
    all_options = []
    if words and isinstance(words, str):
        words = words.split(" ")
        busca = words[len(words)-1]
        vocab = [word.atoken for word in
                 session.query(Word).filter(Word.atoken.like(busca[0]+"%")).all()]
        corrected = spell.correct(busca, vocab)
        parcial = [word.atoken for word in
                   session.query(Word).filter(Word.atoken.like(busca+"%")).all()]
        parcialcorrect = [word.atoken for word in
                          session.query(Word).filter(Word.atoken.like(str(list(corrected)[0])+"%")).all()]
        all_options = set(set(corrected) | set(parcial) | set(parcialcorrect))
    return jsonify(list(all_options))


@app.route('/_filter_documents')
def filter_documents():
    afilter = request.args.get('afilter', 0, type=str)
    collection = session.query(Collection).filter_by(
                                           id=2).one()
    manager = CollectionManager(session, collection)
    result = {}
    if afilter:
        result = manager.filter_documents(afilter+'%', afilter+'%')
    return jsonify(result)


@app.route('/_documents')
def documents():
    collection = session.query(Collection).filter(
            Collection.id == 3).one()
    result = []
    document_list = collection.documents
    for document in document_list:
        result.append({"id": document.id,
                       "title": document.title})
    return jsonify(result)


@app.route('/_document_content/<int:document_id>')
def document_content(document_id):
    one_document = session.query(Document).filter_by(
                        id=document_id).one()
    return jsonify(one_document.contents)


@app.route('/_collections')
def collections():
    collection_list = session.query(Collection).all()
    result = []
    for collection in collection_list:
        result.append({'id': collection.id, 'name': collection.name})
    return jsonify(result)


@app.route('/_set_collection/<int:collection_id>')
def set_collection(collection_id):
    global selected_collection_id
    one_collection = session.query(Collection).filter_by(
                        id=collection_id).one()
    selected_collection_id = one_collection.id
    return jsonify(one_collection.id)


if __name__ == '__main__':
    app.run()
