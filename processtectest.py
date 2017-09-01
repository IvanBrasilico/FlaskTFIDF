# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 09:52:25 2017

@author: ivan

Test module processtec
"""
import processtec as pt

listaTEC = pt.montaTEC()
listaNCM = pt.montaNCM(listaTEC)
listaTECResumo = pt.montaTECResumo(listaNCM)

#Teste
print(listaNCM[0:4])
print(listaTECResumo[0])
list =  pt.tokenize_to_words(listaTECResumo[0])
for word in list:
    print(word)