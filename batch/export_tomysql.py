# Para exportar a tabela de NCMs para a API do AJNA
import os
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

con = sqlite3.connect('../test.db')
SQL_URI = os.environ.get('SQL_URI', 'mysql+pymysql://ivan@localhost:3306/mercante')
engine = create_engine(SQL_URI)

df = pd.read_sql('SELECT * FROM documents WHERE collection_id = 1', con)
df.to_sql('laudo_ncm', engine, if_exists='replace')
# O comando acima pode falhar por erro de caractere inválido.
# A solução é editar collation do campo contents para utf8 e rodar novamente com append
# no lugar de replace
# df.to_sql('laudo_ncm', engine, if_exists='append')
