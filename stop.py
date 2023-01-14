import database
import rest
import config
from datetime import datetime
import flatdict
import logging
import time


class stop_operations:
    def __init__(self, stop_type, stop_id):
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = 'telegram'
        self.token = config.app['stops'][stop_id]['telegram']['token']
        self.rest_get_departures = rest.rest('hsl', 'get_departures')
        self.rest_get_updates = rest.rest(str(self.app), 'get_updates', token=self.token)
        self.rest_send_message = rest.rest(str(self.app), 'send_message', token=self.token)
        self.rest_update_message = rest.rest(str(self.app), 'update_message', token=self.token)
        self.rest_delete_message = rest.rest(str(self.app), 'delete_message', token=self.token)
        self.db = database.database(self.stop_id)
    

    def get_updates(self):
        logging.info("Getting updates related to " + str(self.stop_id))

        # Get existing "//start"-messages from DB
        # Find the latest timestamp

        # Form body
        kwargs = {'offset': offset}
        body = self.get_updates_rest.form_body(kwargs)
        logging.info("Body for update message is " + str(body))

        rest_response = self.get_updates_rest.call()

        # Update database based on response

    def get_departures(self):
        logging.info("Getting departures for " + str(self.stop_id))

        # Request new data set
        new_dataset = self.rest_get_departures.call(stop_type=self.stop_type, stop_id_hsl=self.stop_id_hsl)
        new_dataset = flatdict.FlatDict(new_dataset, delimiter=".")
        new_dataset = new_dataset['data.'+self.stop_type+'.stoptimesWithoutPatterns']
        logging.info("HSL data for " + str(self.stop_id) + " retrieved")

        # Define values based on HSL dataset.
        for departure in new_dataset:
            departure_id = str(self.stop_id) + "_" + str(departure['serviceDay'] + departure['scheduledArrival'])
            departure_time = departure['serviceDay'] + departure['realtimeArrival']
            departure_headsign = departure['headsign']

            # Check if departure is new and add departure to database.
            if self.db.check_if_exists(departure_id) == False:
                logging.info("HSL data for departure " + str(departure_id) + " is new")
                db_data = {'id': departure_id,
                          'time': departure_time,
                          'headsign': departure_headsign,
                          'send_status': False,
                          'message_id': "",
                          'chat_id': "",
                          'text': "",
                          'updated': time.time()}
            else:
                logging.info("HSL data for departure " + str(departure_id) + " is old")
                db_data = {
                           # 'id': departure_id,
                           'time': departure_time,
                           'headsign': departure_headsign,
                           # 'send_status': True,
                           # 'message_id': message_id,
                           # 'chat_id': chat_id,
                           # 'text': text,
                           'updated': time.time()
                           }
            self.db.upsert(departure_id, db_data)
            logging.info("Stored departure " + str(db_data))

    def update_messages(self):
        logging.info("Updating messages for " + str(self.stop_id))       

        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = self.db.search(dead_line, send_status=True)

        if len(db_response) == 0:
            logging.info("No departures to be updated") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']
                chat_id = departure['chat_id']
                message_id = departure['message_id']
                text_from_db = departure['text']

                # Form message
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                logging.info("Message is " + text)

                # Send update only for messages where text has changed
                if text != text_from_db:

                    # Send message
                    self.rest_update_message.call(chat_id=chat_id, message_id=message_id, text=text)

                    # Update data in DB
                    db_data = {
                           # 'id': departure_id,
                           'time': departure_time,
                           'headsign': departure_headsign,
                           # 'send_status': True,
                           # 'chat_id': chat_id,
                           # 'message_id': message_id,
                           'text': text,
                           'updated': time.time()
                           }
                    self.db.upsert(departure_id, db_data)
                    logging.info("Departure " + str(departure_id) + " updated with message details " + str(db_data)) 

    def send_messages(self):
        logging.info("Sending messages for " + str(self.stop_id))

        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = self.db.search(dead_line, send_status=False)

        if len(db_response) == 0:
            logging.info("No new departures to send messages") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']
                chat_id = str(config.app['stops'][self.stop_id][self.app]['chat_id'])
                # message_id = departure['message_id']
                # text_from_db = departure['text']
                
                # Form message
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                logging.info("Message is " + text)

                # Send message
                rest_response = self.rest_send_message.call(chat_id=chat_id, text=text)

                # Update message details to database
                message_id = rest_response['result']['message_id']
                chat_id = rest_response['result']['chat']['id']
                db_data = {
                           # 'id': departure_id,
                           'time': departure_time,
                           'headsign': departure_headsign,
                           'send_status': True,
                           'chat_id': chat_id,
                           'message_id': message_id,
                           'text': text,
                           'updated': time.time()
                           }
                self.db.upsert(departure_id, db_data)
                logging.info("Departure " + str(departure_id) + " updated with message details " + str(db_data))          

    def clean_departures(self):
        logging.info("Cleaning messages and data base for " + str(self.stop_id))

        # Retrieve departures from database
        dead_line = time.time()
        db_response = self.db.search(dead_line)
        
        if len(db_response) == 0:
            logging.info("Nothing to delete for bot " + str(self.stop_id))

        else:
            for departure in db_response:
                departure_id = departure['id']
                # departure_time = departure['time']
                # departure_headsign = departure['headsign']
                chat_id = departure['chat_id']
                message_id = departure['message_id']
                # text_from_db = departure['text']

                # Delete messages
                rest_response = self.rest_delete_message.call(chat_id=chat_id, message_id=message_id)
                logging.info("Response to delete message for " + str(departure_id) + ": " +str(rest_response))

                # Remove from database
                db_response = self.db.delete(departure_id)
                logging.info("Response to delete message for " + str(departure_id) + ": " +str(db_response))

    