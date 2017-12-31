# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 09:52:25 2017

@author: ivan

Test module processtec
"""
import pprint
import time
from pymongo import MongoClient
from pymongo import DeleteMany
import batch.processtec as pt

initial_sec = time.time()


def my_timer(function, description, params=[]):
    """Simple profiling"""
    secs = time.time()
    print(description)
    result = function(*params)
    secse = time.time()
    print('Tempo em segundos: ', secse - secs)
    return result


def mongo_init():
    global collection
    client = MongoClient()
    db = client.tecrank
    collection = db['TEC']


my_timer(mongo_init, 'Mongo initialization')

# collection.remove()
exists = True
# collection, exists = manager.add_collection("TEC")
if not exists:
    listaTEC = my_timer(pt.montaTEC(), 'Montando lista TEC')
    listaNCM = my_timer(pt.montaNCM(listaTEC), 'Montando lista NCM')
    listaTECResumo = my_timer(pt.montaTECResumo(listaNCM),
                              'Montando lista TEC Resumo')
    # Create Documents
    for linha in listaTECResumo:
        codigo = linha[:10]
        descricao = linha[11:]
        words = pt.tokenize_to_words(descricao)
        collection.insert_one({'_id': codigo,
                               'descricao': descricao,
                               'words': words})
        # document = manager.add_document(codigo, descricao)
    # manager.commit()
    # Retrieve documents, process then
    # manager.process_collection(pt.tokenize_to_words) TODO
    # manager.commit()
    # documents = collection.documents
    # manager.process(document, pt.tokenize_to_words)


def vocab():
    # Retrieve vocabulary
    global vocab
    documents = collection.find()
    vocab = set()
    for document in documents:
        vocab.update(set(document['words']))
    print('Vocab', list(vocab)[:10])
    print('Total de palavras: ', len(vocab))


def word_count(words):
    # Find a word
    # Retrieve words total occurrence
    print(collection.find({'words': {'$in': words}}
                          ).count())


# Retrieve documents of a word
def word_find(words):
    print([document['_id'] for document in
           collection.find({'words': {'$in': words}})])

# Retrieve word occurrence per document (Term Frequency - TF - docs_tf)


def tf(words):
    agregates = []
    for word in words:
        agregate = list(collection.aggregate([
            {'$unwind': '$words'},
            { '$match': {'words': word}},
            {'$group':
            {'_id': '$_id',
            'count': {'$sum': 1}}
            }
        ]))
        # pprint.pprint(agregate)
        agregates.append(agregate)
    return agregates


def collection_lenght():
    # Total number of documents (Collection length - C)
    print(collection.count())


def avg_dl():
    # Avg Document length (avgdl)
    agregate = list(collection.aggregate([
        {'$unwind': '$words'},
        {'$group':
         {'_id': 'result',
          'count': {'$sum': 1}}
         }
    ]))

    # pprint.pprint(agregate)
    print('Total de palavras', agregate[0]['count'])
    print('Média', agregate[0]['count'] / collection.count())


words = ['carbonato', 'vestuario']
my_timer(vocab, 'Listando vocabulário')
my_timer(word_count, 'Vezes que carbonato ou vestuario ocorrem:',
         [words])
my_timer(word_find, 'Carbonato ou vestuario ocorrem em:',
         [words])
my_timer(collection_lenght, 'Tamanho da coleção')
my_timer(avg_dl, 'Tamanho médio dos documentos')
my_timer(tf, 'Contagem de palavras por documento', [words])

secse = time.time()
print('Tempo total do script: ', secse - initial_sec)
