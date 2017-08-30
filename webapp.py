# -*- coding: utf-8 -*-
"""
    Collections TFIDF JSON Server
    ~~~~~~~~~~~~~~
    A Flask microservice that serves a JSON for use with a front-end
    like jQuery or React
    The query should contain a phrase of words to be seached
    AND the name of the collection
    The response would be a JSON list of documents
    on the format title, contents, normalized rank
    The rank is a TF-IDF pontuaction of the document on relation to the
    words that are being searched
    The Collection must be fed by another application
    The embedded User Interface is just an example
    Ideally, the User Interface must be another application too, even
    a static served HTML5 Application on React, Vue or plan HTML/CSS/JQUERY
    Initiated from the Flask Oficial website example
    :copyright: (c) 2017 by Ivan Brasilico.
    :license: GPL, see LICENSE for more details.
"""
from flask import Flask, jsonify, render_template, request
from sqlalchemy.orm import sessionmaker
from tecmodels import Collection, Word, Document, WordOccurrence, engine
import spelling_corrector as spell

app = Flask(__name__)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/_rank')
def rank():
    """Get words, return ranked results"""
    collection_name = request.args.get('collection_name', 0, type=str)
    words = request.args.get('words', 0, type=str).split(" ")
    result = []
    collection_name = 'TEC'
    #words = ['paracetamol']
    collection = session.query(Collection).filter_by(name=collection_name).one()
    for word in words:
        one_word = session.query(Word).filter_by(atoken=word).first()
        if one_word:
            for occurrence in session.query(WordOccurrence).filter_by(
                word_id=one_word.id).all():
                document_id = occurrence.document_id
                one_document = session.query(Document).filter_by(
                    id=document_id).first()
                result.append(one_document.as_dict())
    return jsonify(result)

@app.route('/_test')
def test():
    return jsonify([{"title":"1", "contents":"TESTE 1"},
                    {"title":"2", "contents":"TESTE 2" }])

@app.route('/_correct')
def correct():
    """Get words, return ranked results"""
    collection_name = request.args.get('collection_name', 0, type=str)
    words = request.args.get('words', 0, type=str).split(" ")
    busca = words[len(words)-1]
    vocab = [word.atoken for word in
             session.query(Word).filter(Word.atoken.like(busca[0]+"%")).all()]
    corrected = spell.correct(busca, vocab)
    parcial = [word.atoken for word in
               session.query(Word).filter(Word.atoken.like(busca+"%")).all()]
    parcialcorrect = [word.atoken for word in
                      session.query(Word).filter(Word.atoken.like(str(list(corrected)[0])+"%")).all()]
    all_options = set(set(corrected)  | set(parcial) | set(parcialcorrect))
    return jsonify(list(all_options))



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
