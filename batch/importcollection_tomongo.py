# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 09:52:25 2017

@author: ivan

Test module processtec
"""
import pprint
import time
import platform
import re
import subprocess
import os
from collections import Counter, defaultdict
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
    global collection, collection_word
    client = MongoClient()
    db = client.tecrank
    collection = db['TEC']
    collection_word = db['TECwords']


def create_collection():
    word_dict = Counter()
    for linha in listaTECResumo:
        codigo = linha[:10]
        descricao = linha[11:]
        words = pt.tokenize_to_words(descricao)
        collection.insert_one({'_id': codigo,
                               'descricao': descricao,
                               'words': words})
        for word in words:
            word_dict[(codigo, word)] += 1
    for key, value in word_dict.items():
        collection_word.insert_one(
            {'codigo': key[0],
             'word': key[1],
             'frequency': value
             })


my_timer(mongo_init, 'Mongo initialization')

exists = True
# collection, exists = manager.add_collection("TEC")
if not exists:
    collection.remove()
    collection_word.remove()
    listaTEC = my_timer(pt.montaTEC, 'Montando lista TEC')
    listaNCM = my_timer(pt.montaNCM, 'Montando lista NCM', [listaTEC])
    listaTECResumo = my_timer(pt.montaTECResumo,
                              'Montando lista TEC Resumo', [listaNCM])
    # Create Documents
    my_timer(create_collection, 'Criando coleção MongoDB')
    collection.create_index([('words', 1)])
    collection_word.create_index([('codigo', 1), ('word', 1)])

    # document = manager.add_document(codigo, descricao)
    # manager.commit()
    # Retrieve documents, process then
    # manager.process_collection(pt.tokenize_to_words) TODO
    # manager.commit()
    # documents = collection.documents
    # manager.process(document, pt.tokenize_to_words)


def vocab():
    # Retrieve all vocabulary
    documents = collection.find()
    vocabulary = set()
    for document in documents:
        vocabulary.update(set(document['words']))
    print('Vocab ', list(vocabulary)[:10])
    print('Total de palavras: ', len(vocabulary))
    return vocabulary


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
            {'$match': {'words': word}},
            {'$group':
             {'_id': '$_id',
              'count': {'$sum': 1}}
             }
        ]))
        # pprint.pprint(agregate)
        agregates.append(agregate)
    return agregates


def tf2(words):
    adict = defaultdict(dict)
    for document in collection_word.find({'word': {'$in': words}}):
        adict[document['word']][document['codigo']] = document['frequency']
    return adict


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


"""
my_timer(word_count, 'Vezes que carbonato ou vestuario ocorrem:',
         [words])
my_timer(word_find, 'Carbonato ou vestuario ocorrem em:',
         [words])
Sequência necessária para fazer o TF/IDF
Repetidos testes duraram em torno de 1 a 2 segundos no total do
(em um notebook Celeron)
Duas tarefas foram mais custosas:
De 0.2 a 0.8 segundos foram gastos na contagem de palavras do vocabulário
e mais 0.25 segundos para a contagem de ocorrências de cada palavra,
isto sem índices.
Após, foi feito um índice para as palavras do array words:
   # collection.create_index([('words', 1)])
 (ver log de testes em mongo_testes.txt)
Aparentemente, o índice não fez grande diferença neste caso.
Como a previsão é de pouca atualização e muita consulta, isto mostrou a
necessidade de um 'cache' para estes dados, uma tabela para guardar uma chave
palavra, lista de documentos com qtde de ocorrências (collection_word)
Com o uso de collection_word, o tempo de busca por palavra caiu de
1s para 0.16 aproximadamente, para 4 palavras.
Outro ganho é que o tempo de busca anterior era linear à quantidade de palavras.
Agora, com 6 palavras em vez de 4, novos testes subiram apenas de 0.16s para
0.17s, portando a quantidade de palavras impacta muito pouco. Com poucas
otimizações adicionais, certamente será possivelmente responder a consulta a uma
lista de palavras calculando Okapi BM25 em menos de 0.2s em média.
Além disso, usando a função agregate do mongo para contar o número de palavras
do vocabulário, o tempo cai para menos da metade.
"""
print('##################################################')
print('# Testes com uso de tabela RESUMO!!!')
command = "cat /proc/cpuinfo"
all_info = subprocess.check_output(command, shell=True).strip()
all_info = all_info.decode()
for line in all_info.split("\n"):
    if "model name" in line:
        print(re.sub(".*model name.*:", "", line, 1))
print(os.uname())
print(time.strftime('%Y-%m-%d %H:%M'))
words = ['carbonato', 'vestuario', 'paracetamol', 'outros', 'plasticos', 'obras']
print('Words', words)
# vocabulary = my_timer(vocab, '1 - Listando vocabulário e' +
#  ' calculando tamanho (contando cada item da lista)')
my_timer(collection_lenght, '2 - Calculando tamanho da coleção')
my_timer(avg_dl, '3 - Calcular tamanho médio dos documentos')
# my_timer(tf, '4 - Contagem de palavras por documento', [words])
lista = my_timer(tf2, '4 - Contagem de palavras por documento', [words])
print(lista['vestuario'])
secse = time.time()
print('Tempo total do script: ', secse - initial_sec)
print('##################################################')

# pprint.pprint(agregate[:9])
