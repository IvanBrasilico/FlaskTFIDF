# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

Provides common methods for managing a collection of documents

This includes inserting documents, mounting bag of words statistics,
and retrieving tf_idf parameters

It is always necessary to set a collection

@author: IvanBrasilico https://github.com/IvanBrasilico/

"""
from tecmodels import Collection, Document, Word, WordOccurrence
# from sqlalchemy.exc import InterfaceError
from sqlalchemy import func
from sqlalchemy import text
import math
from collections import OrderedDict


class CollectionManager():
    """Manager for a collection. Unique interface for the model classes
    and provides methods for processing docs to index the collection"""
    def __init__(self, psession, pcollection=None):
        self.session = psession
        self.my_collection = pcollection

    def add_collection(self, collection_name):
        """Receives the collection name and sets the collection"""
        self.my_collection = Collection(collection_name)
        self.session.add(self.my_collection)
        self.session.commit()
        return self.my_collection

    def add_document(self, ptitle, pcontent):
        """Receives title and content and adds a document
        to Database related to the Collection already set"""
        one_document = Document(self.my_collection,
                                ptitle, pcontent)
        self.session.add(one_document)
        return one_document

    def add_document_and_proccess(self, ptitle, pcontent, ptokenizer):
        """Receives title and content and adds a document
        to Database related to the Collection already set,
        also calls the process method"""
        document = self.add_document(ptitle, pcontent)
        self.process(document, ptokenizer)

    def process_collection(self, ptokenizer, pengine):
        """ Call process method for all documents"""
        # TODO: make a separate and optimized method to process all
        # documents at once on memory
        Word.__table__.drop(pengine)
        Word.__table__.create(pengine)
        WordOccurrence.__table__.drop(pengine)
        WordOccurrence.__table__.create(pengine)
        for document in self.my_collection.documents:
            self.process(document, ptokenizer)

    def commit(self):
        """Commits all changes. If not executed, the collection
        and the documents will not be saved on the Database"""
        self.session.commit()

    def process(self, pdocument, ptokenizer):
        """ Receives a word token generator and process the document with
        the received function. Adds receiver words to collection for
        statistical analysis
        """
        wordmodellist = []
        wordlist = ptokenizer(pdocument.contents)
        for aword in wordlist:
            # TODO: See best aproach to make unique words (Ignore DBERROR? SEARCH? MEMORY SET?)
            one_word = self.session.query(Word).filter_by(atoken=aword).first()
            if not one_word:
                one_word = Word(aword)
                self.session.add(one_word)
            wordmodellist.append(one_word)
        self.session.commit()

        position = 0
        for one_word in wordmodellist:
            one_occurrence = WordOccurrence(one_word.id, pdocument.id, position)
            self.session.add(one_occurrence)
            position += 1
        self.session.commit()

    def collection_lenght(self):
        """Retrieves total number of documents from Collection"""
        if not self.my_collection:
            return 0
        return self.session.query(func.count('*')).select_from(
            Document).filter(Document.collection_id == self.my_collection.id
                             ).scalar()

    def avg_dl(self):
        """Retrieves average document length from Collection"""
        if not self.my_collection:
            return 0
        conn = self.session.connection()
        sql = text("select avg(doclength) as avgdl from ( " +
                   "select  count(wo.word_id) as doclength " +
                   "from word_occurrences wo inner join " +
                   "documents d on d.id = wo.document_id " +
                   "where d.collection_id = :collection " +
                   "group by wo.document_id);")
        result = conn.execute(sql, collection=self.my_collection.id).fetchone()
        return result['avgdl']

    def tf(self, word):
        """Retrieves from database the list of documents that the word occurs
        and the count of times this happens"""
        # TODO: Insert collection on query
        conn = self.session.connection()
        sql = text("select d.title as title, wo.document_id as docid, " +
                   "count(wo.id) as tf " +
                   "from word_occurrences  wo " +
                   "inner join words w on wo.word_id = w.id " +
                   "inner join documents d on wo.document_id = d.id " +
                   "where w.atoken = :token " +
                   "group by wo.document_id;")
        result = conn.execute(sql, token=word)
        docs_tf = {}
        for row in result:
            docs_tf[row['docid']] = row['tf']
        return docs_tf

    def tf_idf(self, word, k=1.2, b=0.75):
        """Okapi BM25 implementation"""
        C     = self.collection_lenght()
        avgdl = self.avg_dl()
        docs  = self.tf(word)
        ndocs = len(docs)
        idf   = math.log(C - ndocs + 0.5 / ndocs + 0.5)
        score = []
        for docid, tf in docs.items():
            adocument = self.session.query(Document).filter_by(id=docid).one()
            D = avgdl  # adocument.wordcount
            rank = idf * ((tf * (k+1)) / (tf + k + ((1 - b) + (b * D/avgdl))))
            score.append((
                        rank,
                        adocument.title,
                        adocument.contents
            ))
        return sorted(score, key=lambda rank: rank[0], reverse=True)