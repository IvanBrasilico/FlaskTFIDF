# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

Provides common methods for managing a collection of documents

This includes inserting documents, mounting bag of words statistics,
and retrieving tf_idf parameters

It is always necessary to set a collection

A collection can have subcollections based on preprocessing rules.
For example TEC, to be ranked, is beMtter to have the hierarquical structure
joined on a single doc. To be filterer, it is better to stay with the entire
tree original. And then Capítulos, seções e notas can be searched even by rank
or by selection of Capítulo

This class if for implementing methods for managing this collections.
Mouting collection, tokenizing, normalizing, preprocessing, lematize/stemize,
making decisions about filtering and segmentation, ngrams selection, thesaurus,
word vectores, all these are specialized work to be done BEFORE
feeeding this class that are absolutely crucial to posterior success on
searches, classification, and any ML/IR/NLP tasks

@author: IvanBrasilico https://github.com/IvanBrasilico/

"""
import math
from collections import Counter
# from sqlalchemy.exc import InterfaceError
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy import or_
from models.models import Collection, Document, Word, WordOccurrence, CollectionType


class CollectionManager():
    """Manager for a collection. Unique interface for the model classes
    and provides methods for processing docs to index the collection"""
    def __init__(self, psession, pcollection=None):
        self.session = psession
        self.my_collection = pcollection

    def add_collection(self, collection_name):
        """Receives the collection name and retrieve or add the collection
        Returns true if the collection already exists"""
        self.my_collection = self.session.query(Collection).filter(
                                Collection.name == collection_name).first()
        if self.my_collection is not None:
            return self.my_collection, True
        self.my_collection = Collection(collection_name)
        self.session.add(self.my_collection)
        self.session.commit()
        return self.my_collection, False

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
        the received function. Adds received words to collection for
        statistical analysis
        """
        wordmodellist = []
        wordlist = ptokenizer(pdocument.contents)
        doclength = len(wordlist)     # Could be calculated on demand from wo
        pdocument.length = doclength  # Store for better performance
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

    def word_frequency_dict(self, afilter=""):
        """Retrieves from database the absolute frequency from all words
        on all documents for selected collection"""
        # TODO: Insert collection on query
        conn = self.session.connection()
        sql = text("select w.atoken, count(wo.id) as tf " +
                   "from word_occurrences  wo " +
                   "inner join words w on wo.word_id = w.id " +
                   "group by wo.word_id;")
        result = conn.execute(sql)
        docs_tf = {}
        for row in result:
            docs_tf[row['atoken']] = row['tf']
        return docs_tf

    def bm25(self, words, k=1.4, b=0.75):
        """Okapi BM25 implementation"""
        C = self.collection_lenght()
        avgdl = self.avg_dl()
        score = Counter()
        docs = {}
        words = words.split(" ")
        print(words)
        for word in words:
            word = word.strip(' ')
            word = word.lower()
            docs_tf = self.tf(word)
            ndocs = len(docs_tf)
            idf = math.log((C - ndocs + 0.5) / (ndocs + 0.5))
            for docid, tf in docs_tf.items():
                adocument = self.session.query(Document).filter_by(id=docid).one()
                D = adocument.length
                rank = idf * ((tf * (k+1)) / (tf + k + ((1 - b) + (b * D/avgdl))))
                score[docid] += rank
                docs[docid] = adocument
        alist = []
        for docid, doc in docs.items():
            alist.append({'score': score[docid],
                          'title': doc.title,
                          'contents': doc.contents})
        return sorted(alist, key=lambda rank: rank['score'], reverse=True)

    def bm25_cached(self, words, k=1.4, b=0.75):
        """TODO: Create an optimized in memory Okapi BM25 implementation
        This version will retrieve all statistics from the DB
        once when first called (like a Singleton) and mantain it for
        latter calls.
        The statistics will be on arrays and variables for faster
        calculation (otimized for speed, not for memory usage)"""

    def filter_documents(self, title_filter, contents_filter="%"):
        """Traditional SELECT FROM documents WHERE LIKE
        Returns a list of documents"""
        if not self.my_collection:
            return None
        #  Try to choose a child best suited for this type of action
        filter_collection = self.my_collection.get_child_type(
                                                CollectionType.filtered
                                                )
        document_list = self.session.query(Document).filter(
            Document.collection_id == filter_collection.id,
            or_(Document.title.ilike(title_filter),
                Document.contents.ilike(contents_filter))
            ).all()
        result = []
        for document in document_list:
            result.append({"id": document.id, "title": document.title,
                           "contents": document.contents})
        return result

    def list_documents(self):
        """Traditional SELECT id, title FROM documents (ALL)
        Returns a list of documents, only id and title"""
        if not self.my_collection:
            return None
        #  Try to choose a child best suited for this type of action
        filter_collection = self.my_collection.get_child_type(
                                                CollectionType.selection
                                                )
        print(filter_collection.description)
        document_list = filter_collection.documents
        result = []
        for document in document_list:
            result.append({"id": document.id,
                           "title": document.title})
        return result
