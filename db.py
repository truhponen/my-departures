# import logging
import os
from tinydb import TinyDB, Query

# departures_db = os.environ['APP_DIR'] + "/data/departures.json"
departures_db = "./data/departures.json"

def insert(table_id, dataset):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    table.insert(dataset)
    return True

def upsert(table_id, departure_id, dataset):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    db_items = Query()
    table.upsert(dataset, db_items.id == departure_id)
    return True

def update(table_id, departure_id, dataset):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    item = Query()
    results = table.search(item.id == departure_id)
    for result in results:
        print(result)
        print(dataset)
        result.update(dataset)
        return True

def if_value_exists(table_id, id_value):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    evaluation = table.contains(Query().id == id_value)
    return evaluation

def return_based_on_time(table_id, dead_line, is_message_sent):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    departure = Query()
    departures = table.search((departure.time < int(dead_line)) & (departure.send_status == is_message_sent))
    return departures

def drop_tables():
    db = TinyDB(departures_db)
    db.drop_tables()
    return True

def length(table_id):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    table_length = len(table)
    return table_length

def remove(table_id, departure_id):
    db = TinyDB(departures_db)
    table = db.table(table_id)
    departure = Query()
    table.remove(departure.id == departure_id)
    return True
    