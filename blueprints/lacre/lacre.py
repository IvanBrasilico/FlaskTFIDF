#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 11:21:24 2017

@author: ivan
"""
import csv
from flask import Blueprint, jsonify

lacre = Blueprint('lacre', __name__)
containers_file = 'blueprints/lacre/conteiners.csv'


def read_conteiners_csv():
    """Abre a lista a ser trabalhada. Lista deve ser gerada a partir de
    uma extracão do Carga"""
    with open(containers_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        container_list = {}
        for row in reader:
            container_list[row['Conteiner']] = row
        return container_list


@lacre.route('/lacre/_test')
def test():
    """ Simple Mock test. App is alive or not? """
    return jsonify([{"container": "HJCU000000", "lacre": "MGK00001"},
                    {"container": "MSKU1234567", "contents": "MSK12345"}])


@lacre.route('/lacre/_container_autocomplete/<parcial_container_id>')
def lista_container(parcial_container_id):
    """ Para "autocomplete" carrega o csv e filtra campo contêiner"""
    container_list = read_conteiners_csv()
    slice_size = len(parcial_container_id)
    result = [linha for _, linha in container_list.items() if
              linha['Conteiner'][:slice_size] == parcial_container_id]
    return jsonify(result)


@lacre.route('/lacre/_container/<container_id>')
def container(container_id):
    """ Abre csv, procura contêiner, retorna linha ou "não encontrado" """
    container_list = read_conteiners_csv()
    print(container_list)
    try:
        linha = container_list[container_id]
    except KeyError:
        linha = None
    result = []
    if linha is None:
        result.append("Contêiner não encontrado")
    else:
        result.append(linha)
    return jsonify(result)


@lacre.route('/lacre/_lacre/<lacre_id>')
def consulta_lacre(lacre_id):
    """ Abre csv, procura contêiner, retorna linha ou "não encontrado" """
    return jsonify([{"Conteiner": "TESTE", "Lacre": lacre_id}])


@lacre.route('/lacre/_log')
def log():
    """Retorna o conteúdo do arquivo de log"""
    return jsonify([{"line": "This is one log line"}])


@lacre.route('/lacre/_status')
def status():
    """Retorna a lista original menos a lista de verificados, E
    a lista de verificados. Para checagem de progresso"""
    return jsonify([{"containers_restantes":
                    "These are the containers to verifiy"},
                    {"containers_verificados":
                        "These are the containers aleready veirified"}])
