import sqlite3
import io
import traceback
import os
import re
import requests
import json
import time


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


try:
    conn = sqlite3.connect("finland.db")
    conn.row_factory = make_dicts
    sql = "select c.city_id,c.lat,c.lon,cn.city_name from cities c LEFT JOIN  city_names cn on cn.city_id = c.city_id where cn.lang=1"
    cur = conn.execute(sql)
    clist = cur.fetchall()
    cur.close()
    cities = {}
    for c in clist:
        cities[c["city_id"]] = c

    # 13 joensuu 98  helsinki / 440.8 km, 5 h 43 min
    # city1 = 13
    # city2 = 98
    for city1 in range(0, len(cities)):
        for city2 in range(0, city1+1):
            print(f'[{city1}] {cities[city1]["city_name"]}->[{city2}] {cities[city2]["city_name"]}\t', end="")
            # continue
            if city1 == city2:
                dist = 0.0
                tm = 0.0
            else:
                url = f'http://router.project-osrm.org/route/v1/driving/{cities[city1]["lon"]},{cities[city1]["lat"]};{cities[city2]["lon"]},{cities[city2]["lat"]}?overview=false'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()

                    filename = f"C:\Kuljetus\dist\{city1}_{city2}.json"
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=4, sort_keys=True)

                    dist = data["routes"][0]["distance"]
                    tm = data["routes"][0]["duration"]

                else:
                    print(f"Запрос не удался. Статус код: {response.status_code}")
                    exit

            sql = f"insert into dist ('city1','city2','dist','tm') VALUES ({city1},{city2},{dist},{tm});"
            cursor = conn.execute(sql)
            conn.commit()
            if city1 != city2:
                sql = f"insert into dist ('city1','city2','dist','tm') VALUES ({city2},{city1},{dist},{tm});"
                cursor = conn.execute(sql)
                conn.commit()
            print(dist)
            time.sleep(1)
finally:
    conn.close()
