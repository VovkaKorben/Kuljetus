# import sys
# sys.path.append("C:\\SDK\\py")
from internal import app, read_db, log_to_file
import internal, os, io, traceback, json

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, request, session, render_template
import time

import inspect
import my_email
LANG_KEY = "lang_id"
DISTANCE_OK_ID = -100
DISTANCE_UNKNOWN_ID = -101


def send_mail(values):
    message = render_template(
        "mail.html",
        report=values,
    )
    with open("recipients.txt", "r") as recipients_file:
        # sqlite3log.write(f"[{url}] {value}\n")
        recipients = recipients_file.readlines()
    my_email.send_email(message, recipients)
    
    


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


def get_ip(request, input_data):
    return "127 0 0 1"


def get_timestamp(request, input_data):
    return "its time!"


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


def sendapp(params: dict, request, input_data: dict) -> dict:

    def get_global_function(func_name):
        for name, obj in globals().items():
            if name == func_name and inspect.isfunction(obj):
                return globals()[func_name]
        return None

    # {'username': '', 'userphone': '', 'city1': '', 'city2': '', 'usermessage': '', 'sender': 'sendapp'}
    # на входе у нас так же есть lang_id
    # на выход мы отдаем сообщение об ошибке сразу переведенное
    # "error":"#err_user_phone" - это сразу и тэг, куда отдаем перевод
    # и сразу индекс в базе, откуда читаем нужный нам перевод по lang_id
    # print(globals())
    err = None
    values = {}
    with open("fields.json", "r") as file:
        fields = json.load(file)
    for f in fields:

        if f["visible"]:  # видимое поле, должно придти с формы
            if f["id"] not in input_data:
                log_to_file(f"[sendapp]  Field {f['id'].upper()} not found in input data!")
                exit()
            required = f["required"] if "required" in f else 1
            value = input_data[f["id"]].strip()
            if required:

                if len(value) == 0:
                    err = {"id": f["id"], "message_code": f["required_failed_message"]}
                    break

                func_name = f["validation"] if "validation" in f else None
                if func_name is not None:
                    func = get_global_function(func_name)  # Получение функции по имени
                    if func is None:
                        log_to_file(f"[sendapp]  Validation function '{func_name}' specified for field {f['id'].upper()}, but not found!")
                        exit()
                    if not func(value):
                        err = {"id": f["id"], "message_code": f["validation_failed_message"]}
                        break
            values[f["id"]] = value
        else:  # невидимое поле, например IP или текущая дата
            func_name = f["retrieve"] if "retrieve" in f else None
            if func_name is None:
                log_to_file(f"[sendapp]  Retrieve function for invisible field {f['id'].upper()} not specified!")
                break
            func = get_global_function(func_name)  # Получение функции по имени
            if func is None:
                log_to_file(f"[sendapp]  Retrieve function '{func_name}' for invisible field '{f['id'].upper()}' not found.")
                exit()
            values[f["id"]] = func(request, input_data)

    if err is None:

        # готовим запрос в базу на запись

        """for f in fields:
        if f["visible"]:
            values[f["id"]] = input_data[f["id"]]
        else:
            values["ip"] = input_data["ip"]
            values["created"] = int(time.time())
        """
        # формируем запрос
        query = "insert into orders ({0}) values ({1});".format(
            ",".join(list(values.keys())),
            ",".join([":" + str(x) for x in list(values.keys())]),
        )
        # save to DB
        read_db(
            sql_query=query,
            params=values,
            result_required=False,
        )
        log_to_file(values)
        send_mail(values)

        # no errors, save to DB
        # прячем все поля кроме city1 city2
        for f in fields:
            if f["id"] not in ["city1", "city2"] and f["visible"]:
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
                "html": query,
            }
        )

        # стираем все поля из localstorage

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
        result = sendapp(result, request, input_data)
    else:
        pass  # unkn sender

    return jsonify(result)
