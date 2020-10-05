import os
import datetime
import psycopg2
import pandas as pd
from analytics import df_senador, df_resultado_votacion, df_voto

from dotenv import load_dotenv
load_dotenv()


def single_insert(conn, insert_req):
    """ Execute a single INSERT request """

    cursor = conn.cursor()
    try:
        cursor.execute(insert_req)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


connection = psycopg2.connect(os.environ.get("DATABASE_URL"))


def create_table_senador():

    df = df_senador()
    print(df.head())

    query_create_table = """CREATE TABLE IF NOT EXISTS senador (
        senador_id TEXT,
        partido TEXT,
        bloque TEXT,
        senador TEXT      
    );"""

    connection = psycopg2.connect(os.environ.get("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query_create_table)

    for row in df.iterrows():
        print(row[0])
        senador_id = row[1]['senador_id']
        partido = row[1]['partido']
        bloque = row[1]['bloque']
        senador = row[1]['senador']
        print(senador_id, partido, bloque, senador)

        query = """
        INSERT into senador(senador_id, partido, bloque, senador) values('%s', '%s', '%s', '%s');
        """ % (senador_id, partido, bloque, senador)
        single_insert(connection, query)

    connection.close()


def create_table_voto():
    df = df_resultado_votacion()
    df = df[['voto_id', 'date', 'boletin', 'ses_id']]

    query_create_table = """CREATE TABLE IF NOT EXISTS voto (
        voto_id TEXT,
        date DATE,
        boletin TEXT,
        ses_id TEXT
    );"""

    connection = psycopg2.connect(os.environ.get("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query_create_table)

    for row in df.iterrows():
        print(row[0])
        voto_id = row[1]['voto_id']
        date = row[1]['date']
        boletin = row[1]['boletin']
        ses_id = row[1]['ses_id']
        print(voto_id, date, boletin, ses_id)

        query = """
        INSERT into voto(voto_id, date, boletin, ses_id) values('%s', '%s', '%s', '%s');
        """ % (voto_id, date, boletin, ses_id)
        single_insert(connection, query)

    connection.close()


def create_table_resultado_votacion():
    df = df_resultado_votacion()
    print(df.head())

    query_create_table = """CREATE TABLE IF NOT EXISTS resultado_votacion (
        voto_id TEXT,
        si INT,
        no INT,
        abs INT,
        par INT      
    );"""

    connection = psycopg2.connect(os.environ.get("DATABASE_URL"))

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query_create_table)

    for row in df.iterrows():
        print(row[0])
        voto_id = row[1]['voto_id']
        si = row[1]['si']
        no = row[1]['no']
        ab = row[1]['abs']
        par = row[1]['par']
        print(voto_id, si, no, ab, par)

        query = """
        INSERT into resultado_votacion(voto_id, si, no, abs, par) values('%s', %s, %s, %s, %s);
        """ % (voto_id, si, no, ab, par)
        single_insert(connection, query)

    connection.close()


def create_table_voto_senador():
    connection = psycopg2.connect(os.environ.get("DATABASE_URL"))
    df = df_voto()
    print(df.head())

    query_create_table = """CREATE TABLE IF NOT EXISTS voto_senador (
        senador_id TEXT,
        voto_id TEXT,
        voto TEXT     
    );"""

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query_create_table)

    for row in df.iterrows():
        print(row[0])
        senador_id = row[1]['senador_id']
        voto_id = row[1]['voto_id']
        voto = row[1]['voto']

        query = """
        INSERT into voto_senador(senador_id, voto_id, voto) values('%s', '%s', '%s');
        """ % (senador_id, voto_id, voto)
        single_insert(connection, query)

    connection.close()


def main():
    create_table_voto_senador()


if __name__ == "__main__":
    main()
