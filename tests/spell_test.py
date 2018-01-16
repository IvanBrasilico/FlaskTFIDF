# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 16:31:52 2017

@author: IvanBrasilico

"""
import util.spelling_corrector as spell
from sqlalchemy.orm import sessionmaker
from models.models import Word, engine

Session = sessionmaker(bind=engine)
session = Session()

busca = "inicia"

while busca != "":
    busca = input("Digite a palavra a corrigir:")
    vocab = [word.atoken for word in
             session.query(Word).filter(Word.atoken.like(busca[0]+"%")).all()]
    correct = spell.correct(busca, vocab)
    parcial = [word.atoken for word in
               session.query(Word).filter(Word.atoken.like(busca+"%")).all()]
    parcialcorrect = [word.atoken for word in
                      session.query(Word).filter(Word.atoken.like(str(list(correct)[0])+"%")).all()]
    print("Corrigida:"+str(correct))
    print("Parcial:"+str(parcial))
    print("Parcial corrigida:"+str(parcialcorrect))
    all_options = set(set(correct)  | set(parcial) | set(parcialcorrect))
    print("Final:"+str(all_options))
