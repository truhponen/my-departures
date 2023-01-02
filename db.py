# import logging
from tinydb import TinyDB, Query


def insert(table_id, dataset):
    db = TinyDB('db')
    table = db.table(table_id)
    table.insert(dataset)

def if_value_exists(table_id, id_value):
    value = ""
    db = TinyDB('db')
    table = db.table(table_id)
    evaluation = table.contains(Query().id == id_value)
    return evaluation

def drop_tables():
    db = TinyDB('db')
    db.drop_tables()

def length(table_id):

    db = TinyDB('db')
    table = db.table(table_id)
    table_length = len(table)
    return table_length

def remove_based_on_time(table_id, dead_line):

    db = TinyDB('db')
    table = db.table(table_id)
    table.remove(Query().time < int(dead_line))
