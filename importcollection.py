# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

@author: ivan

"""
from tecmodels import db
from collectionmanager import CollectionManager
import processtec as pt

db.drop_all()
db.create_all()

tec = CollectionManager(db.session)
tec.set_collection("TEC")



listaTEC = pt.montaTEC()
listaNCM = pt.montaNCM(listaTEC)
listaTECResumo = pt.montaTECResumo(listaNCM)

for linha in listaTECResumo:
    codigo = linha[:10]
    descricao = linha[11:]
    tec.add_document(codigo, descricao)

tec.commit()
