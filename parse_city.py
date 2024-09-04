import sqlite3
import io
import traceback
import os
import re


def parse_lat_lon(s):
    coord_index = 0


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


try:
    conn = sqlite3.connect("finland.db")
    conn.row_factory = make_dicts

    # парсим города из текстового файла
    cur = conn.execute("select region_name FROM regions WHERE lang=3 ORDER BY region_id")
    reg_list = cur.fetchall()
    cur.close()
    regions = []
    for r in reg_list:
        regions.append(r["region_name"].lower())

    with open("C:\\Kuljetus\\src\\fincity8.txt", "r", encoding="UTF-8") as file:
        while line := file.readline():
            d = line.split("\t")
            d.pop(0)

            try:
                reg_id = regions.index(d[4].lower()) + 1
            except ValueError:
                print(f"No regions for: {d[0]}")
                break

            # print(d)

            # get max ID
            cur = conn.execute("select IFNULL(max(city_id)+1,0) as cid FROM cities")
            cid = cur.fetchall()
            cur.close()
            cid = cid[0]["cid"]

            cursor = conn.execute(f"INSERT into city_names (city_id,city_name,lang,city_name_lower) VALUES ({cid},'{d[0]}',3,'{d[0].lower()}')")
            conn.commit()
            cursor = conn.execute(f"INSERT into city_names (city_id,city_name,lang,city_name_lower) VALUES ({cid},'{d[1]}',1,'{d[1].lower()}')")
            conn.commit()
            cursor = conn.execute(f"INSERT into city_names (city_id,city_name,lang,city_name_lower) VALUES ({cid},'{d[2]}',2,'{d[2].lower()}')")
            conn.commit()

            population = int(re.sub("[^0-9]", "", d[5]))

            # dms = parse_lat_lon(d[7])
            dms = re.split(r"\D+", d[7])
            dms = dms[:-1]
            print(dms)

            d1 = dms[0]
            m1 = dms[1]
            if len(dms) == 6:
                s1 = dms[2]
                d2 = dms[3]
                m2 = dms[4]
                s2 = dms[5]
            else:
                s1 = 0
                d2 = dms[2]
                m2 = dms[3]
                s2 = 0
            lat = int(d1) + int(m1) / 60 + int(s1) / 3600
            lon = int(d2) + int(m2) / 60 + int(s2) / 3600
            print(lat, lon)
            sql = f"INSERT into cities (city_id,city_region,lat,lon,established,population) VALUES ({cid},{reg_id},{lat},{lon},{int(d[6])},{population})"
            cursor = conn.execute(sql)
            conn.commit()

        #   regionID =
        #   cur = conn.execute('SELECT region_id,lang FROM regions')
        #     data = cur.fetchall()
        #     cur.close()
        #   regionID =


finally:
    conn.close()
# return

"""
    добавляет отсутствующие регионы Финляндии
    cur = conn.execute('SELECT region_id,lang FROM regions')
    data = cur.fetchall()
    cur.close()
    v = []
    for d in data:
        v.append(f"{d['region_id']}_{d['lang']}")
    cursor = conn.cursor()
    for r in range(1,20):
        for l in range(0,5):
            x = f"{r}_{l}"
            if x not in v:
                print(x,' ',end=' ')
                # cur = conn.execute('SELECT region_id,lang FROM regions')
                sql = f'INSERT into regions (region_id,lang) VALUES ({r},{l})'
                cursor = conn.execute(sql)
                conn.commit()
    """
