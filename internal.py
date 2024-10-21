from html.parser import HTMLParser
from io import StringIO
from datetime import datetime
import time
from hashlib import md5

import sqlite3
import io
import traceback
import os
from flask import Flask, jsonify, request, g, current_app

DB_FILENAME = "finland.db"

# debug = False
debug = True
app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="static/templates",
)


class db_error(Exception):
    """Base class for other exceptions"""

    pass


def read_db(
    sql_filename=None, sql_query=None, params={}, conn=None
):  # for select sql

    try:
        if sql_filename is not None:
            sqlpath = os.path.join(app.root_path, "static", "sql", sql_filename)
            if not os.path.isfile(sqlpath):
                raise db_error(
                    f"Error while fetching DB\nQuery {sql_filename} not exists!"
                )
            try:
                sqlfile = io.open(sqlpath, mode="r", encoding="utf-8")
                sql_query = sqlfile.read()
            finally:
                sqlfile.close
        elif sql_query is None:
            raise db_error("sql_filename is None and sql_query is None")

        for k in dict(params):
            if type(params[k]) == list:
                v = ",".join([str(x) for x in params[k]])
                sql_query = sql_query.replace(f":{k}", v)
                del params[k]
        if conn is None:
            conn = flask_db_conn()

        cur = conn.execute(sql_query, params)

        try:
            data = cur.fetchall()
        finally:
            cur.close()

    except:
        for line in traceback.format_stack():
            print(line.strip())
        raise db_error(
            f"""
{'-'*60} Error while fetching DB {'-'*60} 
sql_filename: {sql_filename}
sql_query: {sql_query}
{traceback.format_exc()}
{'-'*80} 
            """
        )
        # f"{'-'*60}\nError while fetching DB\nSQL filename: {sql_filename}\n{traceback.format_exc()}\n{'-'*60}"        )
    return data


def sqlite_trace_callback(value):
    # return
    # url = flask.request.base_url
    # url = url.split("/")[-1:]
    # url = url[0]

    value = value.replace("\n", " ")
    while value.find("  ") != -1:
        value = value.replace("  ", " ")

    sqlite3log = open("sqlite3.log", "a")
    # sqlite3log.write(f"[{url}] {value}\n")
    sqlite3log.write(f"{value}\n")
    sqlite3log.close()


def make_dicts(cursor, row):
    return dict(
        (cursor.description[idx][0], value) for idx, value in enumerate(row)
    )


def make_raw(cursor, row):
    return row[0]


"""
def is_flask_app():
    try:
        # Проверяем, есть ли активный контекст приложения
        return current_app is not None
    except RuntimeError:
        # Если возникла ошибка, значит приложение Flask не запущено
        return False
"""


def dbc():
    if "db" not in globals():
        global db
        try:
            dbpath = os.path.join(app.root_path, DB_FILENAME)
            db = sqlite3.connect(dbpath)
            db.row_factory = make_dicts
            if debug:
                db.set_trace_callback(sqlite_trace_callback)

        except:
            return None
    return db


def flask_db_conn():
    if "db" not in g:
        try:
            dbpath = os.path.join(app.root_path, DB_FILENAME)
            g.db = sqlite3.connect(dbpath)
            g.db.row_factory = make_dicts
            if debug:
                g.db.set_trace_callback(sqlite_trace_callback)

        except:
            return None
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()
