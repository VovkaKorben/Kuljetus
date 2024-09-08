from internal import app
import internal, os, io, traceback, json

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, request, session, render_template

SENDER_CITY1 = 11
SENDER_CITY2 = 12
SENDER_INIT = 0
SENDER_LANG = 20


# по заданному ID языка читает все текстовые переводы в нужные DOM-элементы
# также устанавливает значение в localStorage
def update_lang(params: dict, lang: int):
    lang = int(lang)
    params["data"].update({"lang": lang})
    # result["data"].update({"city2": data["city2"]})

    langs = internal.read_db("lang.sql")
    for id in langs:
        params["dom"].append(
            {
                "selector": f"[data-langid='{id['lang']}']",
                "css_add" if id["lang"] == lang else "css_remove": ["selected"],
            }
        )

    transl = internal.read_db("translation.sql", {"lang": lang})
    for i in transl:
        params["dom"].append({"selector": f"[data-lang='{i['dom']}']", "html": i["translation"]})
    return params


@app.route("/")
def main():
    languages = internal.read_db("lang.sql")
    return render_template("main.html", languages=languages)


def city_input(params: dict, cityname: str, elem: str, sender: int) -> dict:
    show = sender != SENDER_INIT

    if show:
        search_cityname = cityname.strip().lower()
        show = len(search_cityname) > 0

    if show:  # check exact name
        search = internal.read_db("cityexact.sql", {"cityname": search_cityname})
        if len(search) == 1:
            show = False

    if show:  # check variants
        search = internal.read_db("citysearch.sql", {"cityname": search_cityname})
        show = len(search) > 0

    if show:
        html = ""
        for i in search:
            html += f"<div data-cityid={ i['city_id'] } class='flex_lc'><span data-text>{i['city_name']}</span><span class='region'>{i['region_name']}</span></div>"
        params["dom"].append({"selector": elem, "html": html, "css_remove": ["dropdown_hide"]})

    if not show:
        params["dom"].append({"selector": elem, "css_add": ["dropdown_hide"]})
    return params


@app.route("/parse_data", methods=["POST"])
def parse_data():
    data = json.loads(request.get_data())
    result = {"dom": [], "data": {}}
    sender = data["sender"] if "sender" in data else 0

    if sender in [SENDER_CITY1]:
        result["data"].update({"city1": data["city1"]})
    if sender in [SENDER_CITY2]:
        result["data"].update({"city2": data["city2"]})
    if sender in [SENDER_CITY1, SENDER_INIT]:
        result = city_input(result, data["city1"], "#city1_dd", sender)
    if sender in [SENDER_CITY2, SENDER_INIT]:
        result = city_input(result, data["city2"], "#city2_dd", sender)
    if sender in [SENDER_LANG, SENDER_INIT]:
        result = update_lang(result, data["lang"])

    # calculate
    mode, city1_name, city2_name, dist = 0, "", "", 0
    city1 = data["city1"].strip()
    if len(city1):
        city1_res = internal.read_db("citydist_prepare.sql", {"city_name": city1.lower()})
        if len(city1_res) == 1:
            mode |= 0x02  # city1 OKзн
            city1_name = city1_res[0]["city_name"]
        else:
            mode |= 0x01  # city1 search error
            city1_name = city1

    city2 = data["city2"].strip()
    if len(city2):
        city2_res = internal.read_db("citydist_prepare.sql", {"city_name": city2.lower()})
        if len(city2_res) == 1:
            mode |= 0x08  # city2 OK
            city2_name = city2_res[0]["city_name"]
        else:
            mode |= 0x04  # city2 search error
            city2_name = city2

    # convert bits to msg index
    mode = [1, 2, 1, 0, 3, 4, 3, 0, 1, 2, 5, 0, 0, 0, 0, 0][mode]  # 0  error 1	intro   2	c1 not found    3	c2 not found    4	c1/c2 not found 5	OK
    # get message from table
    msg = internal.read_db("citydist_message.sql", {"mode": mode, "lang": data["lang"]})
    msg = msg[0]["translation"]
    if mode == 5:
        dist_res = internal.read_db("citydist.sql", {"city1": city1_res[0]["city_id"], "city2": city2_res[0]["city_id"]})
        dist = round(dist_res[0]["dist"] / 1000)
    # if len(dist):
    msg = msg.format(city1=city1_name, city2=city2_name, dist=dist, price=round(dist * 1.3))
    result["dom"].append({"selector": "#calculations", "html": msg})

    return jsonify(result)
