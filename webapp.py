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
    Initiated from the Flask Oficial website example
    :copyright: (c) 2017 by Ivan Brasilico.
    :license: GPL, see LICENSE for more details.
"""
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)


@app.route('/_rank')
def add_numbers():
    """Get words, return ranked results"""
    collection_name = request.args.get('collection_name', 0, type=str)
    words = request.args.get('words', 0, type=str)
    return jsonify([{"result":"TEST1"}, {"result":"TEST2" }])


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

