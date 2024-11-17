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


def log_to_file(msg):
    msg = "[{d}] {m}\n".format(
        d=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        m=msg,
    )
    with open("logfile.txt", "a", encoding="utf-8") as logfile:
        logfile.write(msg)
    print(msg)


class db_error(Exception):
    """Base class for other exceptions"""

    pass


def load_template(templatefilename):
    try:
        templatefilename = os.path.join(app.static_folder, "templates", templatefilename)
        templatefile = io.open(templatefilename, mode="r", encoding="utf-8")
        try:
            templatecontent = templatefile.read()
            return {"error": False, "data": templatecontent}
        finally:
            templatefile.close()
    except:
        err_text = f"error load <b>{templatefilename}</b>:\n{traceback.format_exc()}"
        err_text = "<br />\n".join(err_text.split("\n"))
        return {"error": True, "data": err_text}


def read_sql_file(sqlfilename):
    sqlpath = os.path.join(app.root_path, "static", "sql", sqlfilename)
    # sqlpath = "static/sql/" + sqlfilename
    if not os.path.isfile(sqlpath):
        raise db_error(f"Error in <b>read_db2</b>\nQuery <b>{sqlfilename}</b> not exists!")
    try:
        sqlfile = io.open(sqlpath, mode="r", encoding="utf-8")
        try:
            return sqlfile.read()
        finally:
            sqlfile.close
    except:
        # return {'error': True, 'data': f'Error in <b>read_db2</b>\nFilename: <b>{sqlfilename}</b>\nQuery: <b>{sqlquery}</b>\n{traceback.format_exc()}\n'}
        raise db_error(f"Error in <b>read_sql_file</b>\nSQL filename: <b>{sqlfilename}</b><hr>\n{traceback.format_exc()}\n")


def read_db(
    sql_filename=None,
    sql_query=None,
    params={},
    result_required=True,
    conn=None,
):  # for select sql
    data = None
    try:
        if sql_filename is not None:
            sqlpath = os.path.join(app.root_path, "static", "sql", sql_filename)
            if not os.path.isfile(sqlpath):
                raise db_error(f"Error while fetching DB\nQuery {sql_filename} not exists!")
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
            if result_required:
                data = cur.fetchall()
            else:
                conn.execute("commit;")
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

    with open("sqlite3.log", "a") as sqlite3log:
        # sqlite3log.write(f"[{url}] {value}\n")
        sqlite3log.write(f"{value}\n")
    # sqlite3log.close()


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def make_raw(cursor, row):
    return row[0]


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
