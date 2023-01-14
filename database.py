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

    def upsert(self, departure_id, dataset):
        db_items = Query()
        self.table.upsert(dataset, db_items.id == departure_id)
        return True

    def check_if_exists(self, id_value):
        db_items = Query()
        evaluation = self.table.contains(db_items.id == id_value)
        return evaluation

    def delete(self, departure_id): 
        departure = Query()
        self.table.remove(departure.id == departure_id)
        return True