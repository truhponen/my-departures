# import logging
import os
from tinydb import TinyDB, Query

departures_db = os.environ['APP_DIR'] + "/data/departures.json"

def insert(table_id, dataset):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    table.insert(dataset)
    print(departures_db)

def if_value_exists(table_id, id_value):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    evaluation = table.contains(Query().id == id_value)
    print(departures_db)
    return evaluation

def drop_tables():
    db = TinyDB(departures_db)
    db.drop_tables()
    print(departures_db)

def length(table_id):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    table_length = len(table)
    print(departures_db)
    return table_length

def remove_based_on_time(table_id, dead_line):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    table.remove(Query().time < int(dead_line))
    print(departures_db)