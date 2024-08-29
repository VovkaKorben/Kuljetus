from internal import app
import internal, os, io, traceback, json

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, request, session, render_template


# по заданному ID языка читает все текстовые переводы в нужные DOM-элементы
# также устанавливает значение в localStorage
def update_lang(params: dict, lang_id: int):
    lang_id = int(lang_id)
    params.update_safe({"data": {"lang": lang_id}})
    dom = []

    lang_ids = internal.read_db("lang_id.sql")
    for id in lang_ids:
        dom.append(
            {
                "selector": f"[data-langid='{id['lang_id']}']",
                "css_add" if id["lang_id"] == lang_id else "css_remove": ["selected"],
            }
        )

    transl = internal.read_db("translation.sql", {"lang_id": lang_id})

    for i in transl:
        dom.append({"selector": f"[data-lang='{i['dom']}']", "html": i["translation"]})
    params.update_safe({"dom": dom})
    return params


@app.route("/")
def main():
    # if "lang" in request.cookies:
    #     lang = request.cookies["lang"]
    # else:
    #     lang = 0
    # lang = request.cookies["lang"] if "lang" in request.cookies else 0
    # city1 = request.cookies["city1"] if "city1" in request.cookies else "aaa"
    # city2 = request.cookies["city2"] if "city2" in request.cookies else "bbb"
    # # do something else
    # # session['key'] = 'value'  # Пример добавления данных в сессию
    # # return f"Stored 'key' in session with value: {session['key']}"
    # # template =internal.load_template("main.html")
    # vars = {}
    # # lang
    languages = internal.read_db("lang.sql")
    # # return languages

    return render_template("main.html", languages=languages)
    #    , languages=languages, lang_current=lang, city1=city1, city2=city2)


@app.route("/parse_data", methods=["POST"])
def parse_data():
    result = internal.SafeDictUpdater()
    data = json.loads(request.get_data())
    if "lang" in data:
        result = update_lang(result, data["lang"])
    city_modified = False
    if "city1" in data:
        city_modified = True
        result.update_safe({"data": {"city1": data["city1"]}})
    if "city2" in data:
        city_modified = True
        result.update_safe({"data": {"city2": data["city2"]}})
    if city_modified:
        pass

    return jsonify(result)
