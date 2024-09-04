from html.parser import HTMLParser
from io import StringIO
from datetime import datetime
import time
from hashlib import md5

import sqlite3
import io
import traceback
import os
from flask import Flask, jsonify, request, g



debug = False
# debug = True
app = Flask(__name__, static_url_path="", static_folder="static", template_folder="static/templates")

class SafeDictUpdater(dict):
    def update_safe(self, new_data):
        self._recursive_update(self, new_data)

    def _recursive_update(self, original, new_data):
        for key, value in new_data.items():
            if isinstance(value, dict) and key in original:
                if isinstance(original[key], dict):
                    self._recursive_update(original[key], value)
                else:
                    original[key] = value
            else:
                original[key] = value

    def update(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, dict):
                self.update_safe(arg)
            else:
                raise TypeError(f"Expected dict, got {type(arg).__name__}")
        if kwargs:
            self.update_safe(kwargs)

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


def write_db2(sqlfilename, params, many=False):  # for select sql
    """
    sqlfilename: path to sql query file
    params: dict with params
    """
    sqlpath = "static/sql/" + sqlfilename
    if not os.path.isfile(sqlpath):
        raise db_error(f"Error in <b>write_db2</b>\nQuery <b>{sqlfilename}</b> not exists!")

    conn = get_conn_normal()
    try:
        try:
            sqlfile = io.open(sqlpath, mode="r", encoding="utf-8")
            sqlquery = sqlfile.read()
            c = conn.cursor()
            if many:
                c.executemany(sqlquery, params)
            else:
                c.execute(sqlquery, params)
            conn.commit()
        finally:
            sqlfile.close()
    except:
        msg = f"Error in <b>write_db2</b>\nFilename: {sqlfilename}\nQuery: {sqlquery}\n{traceback.format_exc()}\n"
        print(msg)
        return {"error": True, "data": msg}

    return {"error": False}


def read_db_nofile(sql_query, params, raw=False):
    conn = get_conn_raw() if raw else get_conn_normal()
    try:
        cur = conn.execute(sql_query, params)
        try:
            data = cur.fetchall()
        finally:
            cur.close()
    except:
        raise db_error(f"Error in <b>read_db_nofile</b>\n<hr>\n{traceback.format_exc()}\n")
    return data


def read_sql_file(sqlfilename):
    sqlpath = "static/sql/" + sqlfilename
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


def read_db(sqlfilename, params={}):  # for select sql
    sqlpath = "static/sql/" + sqlfilename
    if not os.path.isfile(sqlpath):
        raise db_error(f"Error while fetching DB\nQuery {sqlfilename} not exists!")

    try:
        sqlfile = io.open(sqlpath, mode="r", encoding="utf-8")
        try:
            sqlquery = sqlfile.read()

            cur = db_conn().execute(sqlquery, params)
            try:
                data = cur.fetchall()
            finally:
                cur.close()
        finally:
            sqlfile.close

    except:

        raise db_error(f"Error while fetching DB\nSQL filename: {sqlfilename}\n{traceback.format_exc()}\n")
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
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def make_raw(cursor, row):
    return row[0]



def db_conn():
    if "db" not in g:
        try:
            g.db = sqlite3.connect("finland.db")
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

