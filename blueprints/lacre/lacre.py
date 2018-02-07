#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 11:21:24 2017

@author: ivan
"""
import csv
import os
from flask import Blueprint, jsonify
from flask import flash, request, redirect, render_template, url_for
from flask_jwt import jwt_required
from werkzeug.utils import secure_filename

lacre = Blueprint('lacre', __name__)
path = os.path.dirname(os.path.abspath(__file__))
containers_file = 'conteiners.csv'
UPLOAD_FOLDER = path
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
memory_log = []
memory_report = {}


@lacre.route('/lacre')
def index():
    return render_template('lacre.html')


@lacre.route('/_lacre/test')
def test():
    """ Simple Mock test. App is alive or not? """
    return jsonify([{"container": "HJCU000000", "lacre": "MGK00001"},
                    {"container": "MSKU1234567", "contents": "MSK12345"}])

def read_conteiners_csv():
    """Abre a lista a ser trabalhada. Lista deve ser gerada a partir de
    uma extracão do Carga"""
    with open(os.path.join(path, containers_file)) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        container_list = {}
        for row in reader:
            container_list[row['Conteiner']] = row
        return container_list


def allowed_file(filename):
    """Check allowed extensions"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@lacre.route('/lacre/upload', methods=['GET', 'POST'])
def upload_file():
    """Função simplificada para upload do arquivo CSV de extração
    Arquivo precisa de uma coluna chamada Conteiner e uma coluna chamada Lacre
    """
    result = ""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            result = 'Não há arquivo.'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            result = 'Não foi selecionado nenhum arquivo.'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            result = 'Arquivo enviado com sucesso!'
            # return redirect(url_for('lacre._uploaded_file', filename=filename))
    return jsonify([result])


@lacre.route('/_lacre/upload', methods=['POST'])
def _uploaded_file():
    '''Função simplificada para upload do arquivo CSV de extração
    Arquivo precisa de uma coluna chamada Conteiner e uma coluna chamada Lacre
    '''
    result = ""
    if request.method == 'POST':
        # check if the post request has the file part.
        if 'file' not in request.files:
            result = 'Arquivo vazio.'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            result = 'Nome de arquivo vazio'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify([result])


@lacre.route('/_lacre/list_files')
@jwt_required()
def list_files():
    """Lista arquivos csv disponíveis para trabalhar
    """
    lista_arquivos = [file for file in
                      os.listdir(UPLOAD_FOLDER) if file.endswith('.csv')]
    return jsonify(lista_arquivos)


def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir)
    return os.path.abspath(path).startswith(basedir)


@lacre.route('/_lacre/delete/file/<filename>')
@jwt_required()
def delete_file(filename):
    """ Recebe nome do arquivo, tenta apagar
    e retorna para página que chamou"""
    filename = secure_filename(filename)
    filepath = os.path.join(path, filename)
    if is_safe_path(path, filepath):
        os.remove(filepath)
    return jsonify("Excluido")


@lacre.route('/_lacre/select/file/<filename>')
@jwt_required()
def select_file(filename):
    """ Recebe nome do arquivo, tenta apagar
    e retorna para página que chamou"""
    filepath = os.path.join(path, filename)
    if is_safe_path(path, filepath):
        global containers_file
        containers_file = filename
    return jsonify(filename)


@lacre.route('/_lacre/container_autocomplete/<parcial_container_id>')
def lista_container(parcial_container_id):
    """ Para "autocomplete" carrega o csv e filtra campo contêiner"""
    container_list = read_conteiners_csv()
    parcial_container_id = parcial_container_id.upper()
    slice_size = len(parcial_container_id)
    result = [conteiner for conteiner, linha in container_list.items() if
              linha['Conteiner'][:slice_size] == parcial_container_id]
    return jsonify(result)


@lacre.route('/_lacre/container/<container_id>')
@jwt_required()
def container(container_id):
    """ Abre csv, procura contêiner, retorna linha ou "não encontrado" """
    container_list = read_conteiners_csv()
    container_id = container_id.upper()
    try:
        linha = container_list[container_id]
    except KeyError:
        linha = None
    result = []
    if linha is None:
        result.append({'Conteiner': 'Não encontrado'})
        memory_log.append({'Conteiner': container_id,
                           'resultado': 'Não encontrado'})
    else:
        result.append(linha)
        memory_log.append({'Conteiner': container_id,
                           'resultado': 'Encontrado'})
    return jsonify(result)


@lacre.route('/_lacre/lacre/<lacre_id>')
@jwt_required()
def consulta_lacre(lacre_id):
    """ Abre csv, procura lacre, retorna linha ou "não encontrado" """
    container_list = read_conteiners_csv()
    lacre_id = lacre_id.upper()
    encontrado = False
    for _, linha in container_list.items():
        if linha['Lacre'] == lacre_id:
            encontrado = True
            break
    result = []
    if not encontrado:
        result.append({'Lacre': 'Não encontrado'})
        memory_log.append({'Lacre': lacre_id,
                           'resultado': 'Não encontrado'})
    else:
        result.append(linha)
        memory_log.append({'Lacre': lacre_id,
                           'resultado': 'Encontrado'})
    return jsonify(result)


@lacre.route('/_lacre/list/log')
@jwt_required()
def log():
    """Retorna o conteúdo da variável de log"""
    return jsonify(memory_log)


@lacre.route('/_lacre/list/report')
@jwt_required()
def report_list():
    """Retorna o conteúdo da variável de report"""
    report = []
    for status in memory_report:
        report.append(status)
        containers = set(memory_report[status])
        for container in containers:
            report.append(container)
    return jsonify(report)


@lacre.route('/_lacre/add/report')
@jwt_required()
def report_add():
    """Atualiza o conteúdo da variável de report"""
    container = request.args.get('container', '', type=str)
    status = request.args.get('status', '', type=str)
    if status in memory_report:
        memory_report[status].append(container)
    else:
        lista = [container]
        memory_report[status] = lista
    return jsonify([])


@lacre.route('/_lacre/status')
def status():
    """Retorna a lista original menos a lista de verificados, E
    a lista de verificados. Para checagem de progresso"""
    return jsonify([{"containers_restantes":
                    "These are the containers to verify"},
                    {"containers_verificados":
                        "These are the containers already verified"}])
