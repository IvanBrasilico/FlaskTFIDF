#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 18:28:17 2017

@author: IvanBrasilico
"""
from flask import jsonify, request, Flask, render_template
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from flask_jwt import JWT, current_identity, jwt_required
from werkzeug.security import safe_str_cmp

from models.models import Collection, Word, Document
from models.models import engine
from models.collectionmanager import CollectionManager
import util.spelling_corrector as spell
#from util.wordcloudmaker import word_cloud_maker
from blueprints.lacre.lacre import lacre
# from blueprints.lacre.lacre import UPLOAD_FOLDER
if __name__ == '__main__':
    app = Flask(__name__, static_url_path='/static')
    CORS(app)
else:
    from webapp import app

app.register_blueprint(lacre)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session = sessionmaker(bind=engine)
session = Session()
selected_collection_id = 1


app.config.update(SECRET_KEY='secret_xxx',
                      JWT_AUTH_URL_RULE='/api/auth')

class User():
    # proxy for a database of users
    user_database = {'lacre': ('lacre', 'lacre')}

    def __init__(self, username, password):
        self.id = username
        self.name = username
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


def authenticate(username, password):
    user_entry = User.get(username)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
        if user and safe_str_cmp(user.password.encode('utf-8'),
                                 password.encode('utf-8')):
            return user
    return None


def identity(payload):
    user = ''
    user_id = payload['identity']
    user_entry = User.get(user_id)
    if user_entry is not None:
        user = User(user_entry[0], user_entry[1])
    return user


jwt = JWT(app, authenticate, identity)



@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

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
    """Get word, return sugestion from vocabulary"""
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
                                           id=selected_collection_id).one()
    manager = CollectionManager(session, collection)
    result = {}
    if afilter:
        result = manager.filter_documents(afilter+'%', afilter+'%')
    return jsonify(result)


@app.route('/_documents')
def documents():
    collection = session.query(Collection).filter_by(
                                           id=selected_collection_id).one()
    manager = CollectionManager(session, collection)
    result = manager.list_documents()
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

"""
@app.route('/_wordcloud')
def wordcloud():
    collection = session.query(Collection).filter_by(
                                           id=selected_collection_id).one()
    manager = CollectionManager(session, collection)
    frequencies = manager.word_frequency_dict()
    cloud_file, mincount, maxcount = word_cloud_maker(frequencies,
                                                      "static/wc.jpg")
    return render_template('wordcloud.html', image=cloud_file,
                           minrange=mincount, maxrange=maxcount)


@app.route('/_wordcloud_range')
def wordcloud_range():
    collection = session.query(Collection).filter_by(
                                           id=selected_collection_id).one()
    manager = CollectionManager(session, collection)
    frequencies = manager.word_frequency_dict()
    minv = int(request.args.get('minv', '1'))
    maxv = int(request.args.get('maxv', '0'))
    print(minv)
    cloud_file, mincount, maxcount = word_cloud_maker(frequencies,
                                     "/var/www/html/static/wc.jpg", minv, maxv)
    return jsonify({'image': cloud_file,
                    'minrange': mincount, 'maxrange': maxcount})
"""

@app.route('/_set_collection/<int:collection_id>')
def set_collection(collection_id):
    global selected_collection_id
    one_collection = session.query(Collection).filter_by(
                        id=collection_id).one()
    selected_collection_id = one_collection.id
    return jsonify(one_collection.id)


if __name__ == '__main__':
    app.run()
