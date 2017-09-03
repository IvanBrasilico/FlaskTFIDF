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
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static') 
CORS(app)
Bootstrap(app)
nav = Nav()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/filter.html')
def filter():
    return render_template('filter.html')


@app.route('/selection.html')
def selection():
    return render_template('selection.html')

@app.route('/collection.html')
def collection():
    return render_template('collection.html')

@nav.navigation()
def mynavbar():
    return Navbar(
        'Collections Finder',
        View('Rank', 'index'),
        View('Filtered', 'filter'),  
        View('Selection', 'selection'),  
        View('Change Collection', 'collection'),
    )
nav.init_app(app)

if __name__ == '__main__':
    app.run()
