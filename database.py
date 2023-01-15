import config
from tinydb import TinyDB, Query


class database:
    
    def __init__(self, table_id):
        self.db = TinyDB(config.db)
        self.table = self.db.table(table_id)

    def search(self, dead_line, **kwargs):
        db_items = Query()
        if 'send_status' in kwargs:
            db_response = self.table.search((db_items.time < int(dead_line)) & (db_items.send_status == kwargs['send_status']))
        else:
            db_response = self.table.search(db_items.time < int(dead_line))
        return db_response

    def search_highest(self, key):
        db_response = self.table.all()
        sort_list = [item[key] for item in db_response]
        sort_list.sort()
        if len(sort_list) > 0:
            return sort_list[-1]
        else:
            return 0

    def upsert(self, id, dataset):
        db_items = Query()
        db_response = self.table.upsert(dataset, db_items.id == id)
        return db_response

    def check_if_exists(self, id_value):
        db_items = Query()
        db_response = self.table.contains(db_items.id == id_value)
        return db_response

    def delete(self, id): 
        db_items = Query()
        db_response = self.table.remove(db_items.id == id)
        return db_response
