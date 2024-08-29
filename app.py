from internal import app
import internal

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, request, session, render_template


# from flask_wtf.csrf import CSRFProtect
import os, io

import traceback
import json
import random
import utils


@app.route("/")
def main():
    if "lang" in request.cookies:
        lang = request.cookies["lang"]
    else:
        lang = 0
    # do something else
    # session['key'] = 'value'  # Пример добавления данных в сессию
    # return f"Stored 'key' in session with value: {session['key']}"
    # template =internal.load_template("main.html")
    vars = {}
    #lang
vars
    languages =  read_db2("main_init\check_user_ingame_v2.sql", {"uid": token_data["uid"], "utc": utc_ms() - DELAY_AFTER_GAMEEND})
    return render_template("main.html")
    return template["data"]

    return "<p>Hello, World!</p>"


@app.route("/cityinput_", methods=["POST"])  # city input
def main_poll_():
    result = {"chat": {}}
    client_data = json.loads(request.get_data())
    token_data = init_token(client_data["token"])
    game_info = read_db2("main_init\check_user_ingame_v2.sql", {"uid": token_data["uid"], "utc": utc_ms() - DELAY_AFTER_GAMEEND})
    if len(game_info) > 0:
        return {"redirect": "/game"}

    # check opponent apply your game, wa are need to redirect
    # result['chat'] = get_chat_data(0, request.form.get('last_msg_id'))
    get_chat_data(result["chat"], 0, client_data["last_msg_id"])
    result["waitlist"] = get_waitlist_data(token_data["uid"], client_data["waitlist"])

    return jsonify(result)
