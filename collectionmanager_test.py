# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 20:54:36 2017

@author: ivan https://github.com/IvanBrasilico/
"""
from sqlalchemy.orm import sessionmaker
from tecmodels import engine, Collection
from collectionmanager import CollectionManager

Session = sessionmaker(bind=engine)
session = Session()

teccollection = session.query(Collection).filter_by(id=1).one()

manager = CollectionManager(session, teccollection)

print("Collection lenght: "+str(manager.collection_lenght()))
print("Average Document Length: "+str(manager.avg_dl()))
print("Term Frequency (times that appears per document for word 'plastico')")
print(manager.tf('arruelas'))
finaldict = manager.tf_idf('arruelas')
print(finaldict)
print(len(finaldict))

