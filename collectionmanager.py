# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

@author: ivan

"""
from tecmodels import Collection, Document, Word, WordOccurrence

class CollectionManager():
    """Manager for a collection. Unique interface for the model classes
    and provides methods for processing docs to index the collection"""
    session = None

    def __init__(self, psession):
        self.session = psession

    def set_collection(self, collection_name):
        """Receives the collection name and sets the collection"""
        self.my_collection = Collection(collection_name)
        self.session.add(self.my_collection)

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


    def process_collection(self, ptokenizer):
        """ Call process method for all documents"""
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
        for word in ptokenizer(pdocument.contents):
            # TODO: See best aproach to make unique words (Ignore DBERROR? SEARCH? MEMORY SET?)
            one_word = Word(word)
            self.session.add(one_word)
            one_occurrence = WordOccurrence(pdocument, one_word, 0)
            self.session.add(one_occurrence)
