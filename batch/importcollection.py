# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

@author: ivan

"""
from sqlalchemy.orm import sessionmaker
from models.models import engine
from models.collectionmanager import CollectionManager
import batch.processtec as pt

listaTEC = pt.leTEC()
listaNCM = pt.montaNCM(listaTEC)
listaTECResumo = pt.montaTECResumo(listaNCM)
listaCapitulos = pt.montaCapitulos(listaTEC)


# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

manager = CollectionManager(session)

# Cria Collection principal - TEC Resumo
collection, exists = manager.add_collection("TEC")
if not exists:
    # Create Documents
    for linha in listaTECResumo:
        codigo = linha[:10]
        descricao = linha[11:]
        document = manager.add_document(codigo, descricao)
    manager.commit()
    # Retrieve documents, process then
    # manager.process_collection(pt.tokenize_to_words) TODO
    # manager.commit()
    documents = collection.documents
    for document in documents:
        manager.process(document, pt.tokenize_to_words)

# Cria Collection filtragem: Tabela NCM
collection2, exists = manager.add_collection("TEC NCM")
collection2.parent_id = collection.id
collection2.collectiontype = 2
collection2.description = "Tabela NCM hierárquica"
session.commit()
if not exists:
    # Create Documents
    for linha in listaNCM:
        document = manager.add_document(linha[0], linha[1]+' - '+linha[2])
    manager.commit()

# Cria Collection Capitulos
collection3, exists = manager.add_collection("TEC Capitulo")
collection3.parent_id = collection.id
collection3.collectiontype = 3
collection3.description = "Tabela NCM de seleção de Capítulos e Notas"
session.commit()
if not exists:
    # Create Documents
    for linha in listaCapitulos:
        document = manager.add_document(linha[0], linha[1]+' <br> '+linha[2])
    manager.commit()
