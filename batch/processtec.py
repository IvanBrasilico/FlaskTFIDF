# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 22:58:11 2017

@author: ivan
"""
import nltk
import re
from unicodedata import normalize
import os

stopwords = nltk.corpus.stopwords.words('portuguese')


def remover_acentos(txt):
    return normalize('NFKD', txt).encode(
                     'ASCII', 'ignore').decode('ASCII')


def somente_letras_e_numeros(raw):
    raw = remover_acentos(raw)
    clean = re.sub("[^a-zA-Z0-9]", " ", raw)
    return clean


def leTEC(filename=os.path.dirname(__file__)+"/tec.txt"):
    with open(filename) as arq:
        listaarquivoTEC = arq.readlines()
    return listaarquivoTEC


def montaCapitulos(plistaTEC):
    listaCapitulos = []
    r = 0
    while r < len(plistaTEC):
        linha = plistaTEC[r]
        if linha[0:3] == "Cap":  # Procura capítulos
            capitulo = linha
            descricao = ""
            r = r + 1
            linha = plistaTEC[r]
            while linha[0:4] != "Nota":
                descricao = descricao + linha + " "
                r = r + 1
                linha = plistaTEC[r]
            notas = ""
            r = r + 1
            linha = plistaTEC[r]
            while linha[0:4] != "____":
                notas = notas + linha + "\n"
                r = r + 1
                linha = plistaTEC[r]
            listaCapitulos.append([capitulo.strip(), descricao.strip(), notas])
        r = r + 1

    return listaCapitulos


def montaNCM(plistaTEC):
    listaNCM = []
    r = 0
    while r < len(plistaTEC):
        linha = plistaTEC[r]
        if len(linha) < 12:
            i = linha.find(".")
            if ((i >= 2) and (linha[0].isnumeric())):
                r = r + 1
                linha2 = plistaTEC[r]
                # Elimina as sequências de números (na parte 5 Regra de
                # Tributação para Produtos do Setor Aeronáutico da TEC)
                # Primeiro testa se linha não está vazia, depois, se é número
                if (not linha2 == "\n"):
                    if (not linha2[0].isnumeric()):
                        ncm = linha
                        descricao = linha2
                        linha3 = plistaTEC[r+1]
                        tec = ""
                        if ((not linha3) or (linha3[0].isnumeric())):
                            r = r + 1
                            tec = linha3
                        listaNCM.append([ncm.strip(),
                                         descricao.strip(), tec.strip()])
        r = r + 1
    return listaNCM


def montaTECResumo(plistaNCM):
    """ Monta linhas da TEC que contém II com descrição contendo a
    concatenação da descrição da linha e dos "pais"
    - posições, subposições, etc."""
    listaTECResumo = []
    r = 0
    while r < len(plistaNCM):
        linha = plistaNCM[r]
        II = linha[2]
        if (not II == ''):  # É uma Classificação válida/"escolhível", buscar os "pais"
            codigo = linha[0]
            descricao = linha[1]
            s = r - 1
            while True:     # Loop DNA. Percorre a lista "para cima"
                            # procurando a árvore genealógica...
                linha = plistaNCM[s]
                codigo2 = linha[0]
                descricao2 = linha[1]
                lcodigo = codigo[0:2] + "." + codigo[2:4]
                if lcodigo == codigo2:
                    descricao = descricao + " " + descricao2
                    listaTECResumo.append(codigo + " " + descricao)
                    break
                lcodigo = codigo[0:6]
                if lcodigo == codigo2:
                    descricao = descricao + " " + descricao2
                lcodigo = codigo[0:7]
                if lcodigo == codigo2:
                    descricao = descricao + " " + descricao2
                lcodigo = codigo[0:8]
                if lcodigo == codigo2:
                    descricao = descricao + " " + descricao2
                lcodigo = codigo[0:9]
                if lcodigo == codigo2:
                    descricao = descricao + " " + descricao2
                s = s - 1
                if ((s == -1) or ((r - s) > 100)):  #Exceção encontrada, abortar!
                    listaTECResumo.append(codigo+" "+descricao)
                    break
        r = r + 1
    return listaTECResumo


def tokenize_to_words(sentence, splitter=" "):
    """Generator of words tokens
    Usage: for word in tokenize_to_words("Tinha uma pedra no meio do caminho", " "):
               do something
    """
    listofwords = sentence.split(splitter)
    result = []
    for word in listofwords:
        if ((len(word) > 3) and (stopwords.count(word) == 0)):
            word = somente_letras_e_numeros(word)  # Tira tudo que não for A-B e 0-9
            word = word.strip().lower()
            result.append(word)
    return result
