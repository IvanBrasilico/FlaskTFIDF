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
    a static served HTML5 Application on React, Vue or plain HTML/CSS/JQUERY
    Initiated from the Flask Oficial website example
    :copyright: (c) 2017 by Ivan Brasilico.
    :license: GPL, see LICENSE for more details.
"""
from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from sqlalchemy.orm import sessionmaker
from tecmodels import Collection, Word  # , Document, WordOccurrence
from tecmodels import engine
import spelling_corrector as spell
import processtec as pt
from collectionmanager import CollectionManager

app = Flask(__name__)
Bootstrap(app)
nav = Nav()

Session = sessionmaker(bind=engine)
session = Session()

listaTEC = pt.montaTEC()
listaNCM = pt.montaNCM(listaTEC)


@app.route('/_rank')
def rank():
    """Get words, return ranked results"""
    collection_name = request.args.get('collection_name', 0, type=str)
    words = request.args.get('words', 0, type=str)
    result = []
    collection_name = 'TEC'
    collection = session.query(Collection).filter_by(name=collection_name).one()
    manager = CollectionManager(session, collection)
    result = manager.tf_idf(words)
    """for word in words:
        one_word = session.query(Word).filter_by(atoken=word).first()
        if one_word:
            for occurrence in session.query(WordOccurrence).filter_by(
                word_id=one_word.id).all():
                document_id = occurrence.document_id
                one_document = session.query(Document).filter_by(
                    id=document_id).first()
                result.append(one_document.as_dict())
                """
    return jsonify(result)


@app.route('/_test')
def test():
    return jsonify([{"title": "1", "contents": "TESTE 1"},
                    {"title": "2", "contents": "TESTE 2" }])


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
    all_options = set(set(corrected) | set(parcial) | set(parcialcorrect))
    return jsonify(list(all_options))


@app.route('/_filter_documents')
def filter_documents():
    collection_name = request.args.get('collection_name', 0, type=str)
    afilter = request.args.get('afilter', 0, type=str)
    collection_name = 'TEC'
    collection = session.query(Collection).filter_by(name=collection_name).one()
    manager = CollectionManager(session, collection)
    result = manager.filter_documents(afilter+'%', afilter+'%')
    return jsonify(result)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/indexold')
def indexold():
    return render_template('indexold.html')


@app.route('/ncm')
def ncm():
    return render_template('tabelancm.html', ncm=listaNCM)


@app.route('/filter')
def filter():
    return render_template('filter.html')


@nav.navigation()
def mynavbar():
    return Navbar(
        'Collections Finder',
        View('Rank', 'index'),
        View('Filtered', 'filter'),
        View('Change Collection', 'ncm'),
    )
nav.init_app(app)

if __name__ == '__main__':
    app.run()
