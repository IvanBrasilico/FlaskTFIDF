# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

@author: ivan

"""
from sqlalchemy.orm import sessionmaker
from tecmodels import Base, engine
from collectionmanager import CollectionManager
import processtec as pt

listaTEC = pt.montaTEC()
listaNCM = pt.montaNCM(listaTEC)
listaTECResumo = pt.montaTECResumo(listaNCM)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

tec = CollectionManager(session)
collection = tec.set_collection("TEC")

#Create Documents
for linha in listaTECResumo:
    codigo = linha[:10]
    descricao = linha[11:]
    document = tec.add_document(codigo, descricao)
tec.commit()

#tec.process_collection(pt.tokenize_to_words) TODO
#tec.commit()

# Retrieve documents, process then
documents = collection.documents
for document in documents:
    tec.process(document, pt.tokenize_to_words)

