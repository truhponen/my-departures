import config
# import logging
import os
from tinydb import TinyDB, Query, where
import operator
from operator import eq, ge, gt, le, lt, ne
import sys

def insert(table_id, dataset):
    db = TinyDB(config.db)
    table = db.table(table_id)
    table.insert(dataset)
    return True

def upsert(table_id, departure_id, dataset):
    db = TinyDB(config.db)
    table = db.table(table_id)
    db_items = Query()
    table.upsert(dataset, db_items.id == departure_id)
    return True

def update(table_id, departure_id, dataset):
    db = TinyDB(config.db)
    table = db.table(table_id)
    item = Query()
    results = table.search(item.id == departure_id)
    for result in results:
        result.update(dataset)
        return True

def if_value_exists(table_id, id_value):
    db = TinyDB(config.db)
    table = db.table(table_id)
    evaluation = table.contains(Query().id == id_value)
    return evaluation

def return_based_on_time(table_id, dead_line, is_message_sent):
    db = TinyDB(config.db)
    table = db.table(table_id)
    departure = Query()
    departures = table.search((departure.time < int(dead_line)) & (departure.send_status == is_message_sent))
    return departures

def drop_tables():
    db = TinyDB(config.db)
    db.drop_tables()
    return True

def length(table_id):
    db = TinyDB(config.db)
    table = db.table(table_id)
    table_length = len(table)
    return table_length

def remove(table_id, departure_id):
    db = TinyDB(config.db)
    table = db.table(table_id)
    departure = Query()
    table.remove(departure.id == departure_id)
    return True

"""
def search(table_id, **kwargs):
    db = TinyDB(config.db)
    table = db.table(table_id)
    departure = Query()
    departures = {}
    for arg in kwargs:
        if arg == 'less_or_equal'
            departures = table.search(departure.arg < kwargs[arg])
    return departures
"""
operators = {
    "==": 'eq',
    "!=": 'ne',
    "<=": 'le',
    ">=": 'ge',
    "<": 'lt',
    ">": 'gt',
}


def search(table_id, key, oper, value):
    op = operators[oper]
    db = TinyDB(config.db)
    table = db.table(table_id)
    query = Query()
    func = getattr(operator,op)
    term = func(query[key],value)
    departures = table.search(term)
    return departures

print(search("HSL_1000103", 'time', '<=', 1673460859))
print(operator.and_(operator.eq(1,1),operator.eq(1,2)))