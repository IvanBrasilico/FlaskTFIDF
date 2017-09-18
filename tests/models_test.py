# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 20:54:36 2017

@author: ivan https://github.com/IvanBrasilico/
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Collection, Document, Word, WordOccurrence, Base


path = os.path.dirname(os.path.abspath(__file__))
print(path)
engine = create_engine('sqlite:////'+path+'/testmodel.db')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

collection = Collection('TESTE')
session.add(collection)
session.commit()

document1 = Document(collection, 'DOC1', 'Test of document number 1')
document2 = Document(collection, 'DOC2', 'Test of document number 2')
session.add(document1)
session.add(document2)
session.commit()

word1 = Word('Test')
word2 = Word('document')
word3 = Word('number')
session.add(word1)
session.add(word2)
session.add(word3)
session.commit()

wo1 = WordOccurrence(word1.id, document1.id, 1)
wo2 = WordOccurrence(word2.id, document1.id, 2)
wo3 = WordOccurrence(word3.id, document1.id, 3)
wo4 = WordOccurrence(word1.id, document2.id, 1)
wo5 = WordOccurrence(word2.id, document2.id, 2)
wo6 = WordOccurrence(word3.id, document2.id, 3)
session.add(wo1)
session.add(wo2)
session.add(wo3)
session.add(wo4)
session.add(wo5)
session.add(wo6)
session.commit()


# Test the retrieval:

retrieved_collection = session.query(Collection).filter(
                                Collection.name == collection.name).first()

print(retrieved_collection)

for document in retrieved_collection.documents:
    print(document)
