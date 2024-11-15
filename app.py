# import sys
# sys.path.append("C:\\SDK\\py")
from internal import app, read_db
import internal, os, io, traceback, json

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, request, session, render_template
import time

import inspect

LANG_KEY = "lang_id"
DISTANCE_OK_ID = -100
DISTANCE_UNKNOWN_ID = -101


def phone_ok(phone_no: str) -> bool:
    collected = ""
    for c in phone_no:
        if c.isdigit:
            collected += c
    result = len(collected) in [10, 12]

    return result


def city_ok(city_name: str) -> bool:
    search = read_db(
        sql_filename="city/cityexact.sql",
        params={"cityname": city_name.strip().lower()},
    )
    return len(search) == 1


def date_ok(date: str) -> bool:
    return True


# если в params full==1, то выдаем полный перевод
# так же в любом случае выдаем перевод для расчёта дистанции


def update_lang(params: dict, input: dict):
    # setup languages icons
    langs = read_db(sql_filename="lang/language_list.sql")
    for lang in langs:
        css_mode = "css_add" if lang["language_id"] == input["lang_id"] else "css_remove"
        params["dom"].append(
            {
                "selector": f"[data-langid='{lang['language_id']}']",
                css_mode: ["lang_selected"],
            }
        )
    # вычисляем дистанцию
    dist = read_db(
        sql_filename="dist/dist.sql",
        params={
            "city1": input["city1"].strip().lower(),
            "city2": input["city2"].strip().lower(),
        },
    )
    selector_id = DISTANCE_UNKNOWN_ID if len(dist) == 0 else DISTANCE_OK_ID
    transl = read_db(
        sql_filename="lang/get_msg.sql",
        params={
            "language_id": input["lang_id"],
            "selector_id": selector_id,
        },
    )
    # форматируем полученное сообщение о дистанции
    if selector_id == DISTANCE_OK_ID:
        if len(transl) == 0:
            print(f"[update_lang] No translation found selector_id: {selector_id} and lang_id: {input['lang_id']}")
            exit()
        # transl[0]["translation"] = json.dumps(transl[0], ensure_ascii=False)
        transl[0]["translation"] += " (formatted)"

    # добавляем остальной перевод, при необходимости
    if input["full"]:
        transl.extend(
            read_db(
                sql_filename="lang/translation.sql",
                params={"lang_id": input["lang_id"]},
            )
        )

    # переводим полученные элементы в формат, понятный JS
    for item in transl:

        value = {"selector": item["selector_name"]}
        if item["attr"] is None:
            value["html"] = item["translation"]
        else:
            value["attr_set"] = [{"attr": item["attr"], "value": item["translation"]}]
        params["dom"].append(value)

    return params


@app.route("/")
def main():

    languages = internal.read_db(
        sql_filename="lang/language_list.sql",
    )
    with open("fields.json", "r") as file:
        fields = json.load(file)
    return render_template(
        "main.html",
        languages=languages,
        fields=fields,
    )


def city_input(params: dict, value: str, sender: str) -> dict:
    search_value = value.strip().lower()
    show_dropdown_list = len(search_value) > 0

    if show_dropdown_list:  # check exact name
        search = read_db(
            sql_filename="city/cityexact.sql",
            params={"cityname": search_value},
        )
        if len(search) == 1:
            show_dropdown_list = False

    if show_dropdown_list:  # check variants
        search = internal.read_db(
            sql_filename="city/citysearch.sql",
            params={"cityname": search_value},
        )
        show_dropdown_list = len(search) > 0

    selector = f"#{sender} .dropdown_list"
    if show_dropdown_list:
        html = render_template(
            "dropdown.html",
            search=search,
        )
        params["dom"].append(
            {
                "selector": selector,
                "html": html,
                "css_remove": ["hide"],
            }
        )

    else:
        params["dom"].append(
            {
                "selector": selector,
                "css_add": ["hide"],
            }
        )
    return params


def sendapp(params: dict, input_data: dict) -> dict:

    def is_function_available(func_name):
        for name, obj in globals().items():
            if name == func_name and inspect.isfunction(obj):
                return True
        return False

    # {'username': '', 'userphone': '', 'city1': '', 'city2': '', 'usermessage': '', 'sender': 'sendapp'}
    # на входе у нас так же есть lang_id
    # на выход мы отдаем сообщение об ошибке сразу переведенное
    # "error":"#err_user_phone" - это сразу и тэг, куда отдаем перевод
    # и сразу индекс в базе, откуда читаем нужный нам перевод по lang_id
    # print(globals())
    err = None
    with open("fields.json", "r") as file:
        fields = json.load(file)
    for f in fields:
        if f["id"] not in input_data:
            print(f"[sendapp]  Field {f['id'].upper()} not found in input data!")
            exit()
        required = f["required"] if "required" in f else 1
        if required:

            value = input_data[f["id"]].strip()
            if len(value) == 0:
                err = {"id": f["id"], "message_code": f["required_failed_message"]}
                break

            func_name = f["validation"] if "validation" in f else None
            if func_name is not None:
                if not is_function_available(func_name):
                    print(f"[sendapp]  Validation function '{func_name}' specified for field {f['id'].upper()}, but function not found!")
                    exit()
                func = globals()[func_name]  # Получение функции по имени
                if not func(value):
                    err = {"id": f["id"], "message_code": f["validation_failed_message"]}
                    break

    if err is None:
        # no errors, save to DB
        # прячем все поля кроме city1 city2
        for f in fields:
            if f["id"] not in ["city1", "city2"]:
                params["dom"].append(
                    {
                        "selector": f"#{f['id']}",
                        "css_add": ["hide"],
                    }
                )
        # кнопку тоже прячем
        params["dom"].append(
            {
                "selector": "#sendapp",
                "css_add": ["hide"],
            }
        )
        # показываем сообщение об отправке
        params["dom"].append(
            {
                "selector": "#senddone",
                "css_remove": ["hide"],
                "html": "app send done",
            }
        )
        # стираем все поля из localstorage

        # готовим запрос в базу на запись
        values = {}
        for f in fields:
            values[f["id"]] = input_data[f["id"]]
        values["ip"] = input_data["ip"]
        values["created"] = int(time.time())

        # формируем запрос
        query = "insert into orders ({0}) values ({1});".format(
            ",".join(list(values.keys())),
            ",".join([":" + str(x) for x in list(values.keys())]),
        )
        read_db(
            sql_query=query,
            params=values,
            result_required=False,
        )
        params["dom"].append(
            {
                "selector": "#senddone",
                "css_remove": ["hide"],
                "html": query,
            }
        )
    else:
        # читаем сообщение об ошибке из базы
        msg = read_db(
            sql_filename="lang/get_msg.sql",
            params={"language_id": input_data["lang"], "selector_id": err["message_code"]},
        )
        # если сообщения нет - выводим заглушку
        if len(msg) == 0:
            msg = f"Msg for lang {input_data['lang']} and with code {err['message_code']} is absent in DB!"
        else:
            msg = msg[0]["translation"]
        # рисуем сообщение
        params["dom"].append(
            {
                "selector": f"#{err['id']} .err",
                "html": msg,
            }
        )
        # прячем все другие сообщения кроме нужного
        for f in fields:
            if f["id"] == err["id"]:
                mode = "css_remove"
            else:
                mode = "css_add"

            params["dom"].append(
                {
                    "selector": f"#{f['id']} .err",
                    mode: ["hide"],
                }
            )

    return params


@app.route("/parse_data", methods=["POST"])
def parse_data():
    input_data = json.loads(request.get_data())
    result = {
        "dom": [],
        "storage": {},
    }
    sender = input_data["sender"].upper()
    if sender == "LANG":
        result = update_lang(result, input_data)

    elif sender == "CITY1" or sender == "CITY2":
        value = input_data["city1"] if sender == "CITY1" else input_data["city2"]
        result = city_input(result, value, input_data["sender"])
        # city_res = internal.read_db(
        #     sql_filename="citydist_prepare.sql",
        #     params={"city_name": value.lower()},
        # )

    elif sender == "SENDAPP":
        input_data["ip"] = request.remote_addr
        result = sendapp(result, input_data)
    else:
        pass  # unkn sender

    return jsonify(result)
