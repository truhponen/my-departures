import db
import bot_rest
import config
from datetime import datetime
import flatdict
import logging
import time


class bot_operations:
    def __init__(self, name, stop_type, stop_id):
        self.name = name
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = config.app['stops'][stop_id]['app'].lower()
        self.token = config.app['stops'][stop_id]['token']
        self.get_departures_rest = bot_rest.rest('hsl', 'get_departures')
        self.get_updates_rest = bot_rest.rest(str(self.app), 'get_updates', token=self.token)
        self.send_message_rest = bot_rest.rest(str(self.app), 'send_message', token=self.token)
        self.update_message_rest = bot_rest.rest(str(self.app), 'update_message', token=self.token)
        self.clear_departures_rest = bot_rest.rest(str(self.app), 'delete_message', token=self.token)
    

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
        new_dataset = self.get_departures_rest.call(stop_type=self.stop_type, stop_id_hsl=self.stop_id_hsl)
        new_dataset = flatdict.FlatDict(new_dataset, delimiter=".")
        new_dataset = new_dataset['data.'+self.stop_type+'.stoptimesWithoutPatterns']
        logging.info("HSL data for " + str(self.stop_id) + " retrieved")

        # Define values based on HSL dataset.
        for departure in new_dataset:
            departure_id = str(self.stop_id) + "_" + str(departure['serviceDay'] + departure['scheduledArrival'])
            departure_time = departure['serviceDay'] + departure['realtimeArrival']
            departure_headsign = departure['headsign']

            # Check if departure is new and add departure to database.
            if db.if_value_exists(self.stop_id, departure_id) == False:
                logging.info("HSL data for departure " + str(departure_id) + " is new")
                db_data = {'id': departure_id,
                          'time': departure_time,
                          'headsign': departure_headsign,
                          'send_status': False,
                          'message_id': "",
                          'chat_id': "",
                          'text': "",
                          'updated': time.time()}
                db.upsert(self.stop_id, departure_id, db_data)
                logging.info("Stored departure " + str(db_data))

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
                db.upsert(self.stop_id, departure_id, db_data)
                logging.info("Stored departure " + str(db_data))

    def send_messages(self):
        logging.info("Sending messages for " + str(self.stop_id))

        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = db.return_based_on_time(self.stop_id, dead_line, False)

        if len(db_response) == 0:
            logging.info("No new departures to send messages") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']

                # Get chat_ids from DB
                # For chat_id in chat_ids:
                chat_id=str(config.app['stops'][self.stop_id]['chat_id'])
                
                # Form message
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                logging.info("Message is " + text)

                # Send message
                rest_response = self.send_message_rest.call(chat_id=chat_id, text=text)

                # Update message details to database
                message_id = rest_response['result']['message_id']
                chat_id = rest_response['result']['chat']['id']
                db_data = {
                           # 'id': departure_id,
                           'time': departure_time,
                           'headsign': departure_headsign,
                           'send_status': True,
                           'message_id': message_id,
                           'chat_id': chat_id,
                           'text': text,
                           'updated': time.time()
                           }
                db.upsert(self.stop_id, departure_id, db_data)
                logging.info("Departure " + str(departure_id) + " updated with message details " + str(db_data))          

    def update_message(self):
        logging.info("Updating messages for " + str(self.stop_id))       

        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = db.return_based_on_time(self.stop_id, dead_line, True)

        if len(db_response) == 0:
            logging.info("No departures to be updated") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']
                message_id = departure['message_id']
                chat_id = departure['chat_id']
                text_from_db = departure['text']

                # Form message
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                logging.info("Message is " + text)

                if text != text_from_db:

                    # Send message
                    self.update_message_rest.call(chat_id=chat_id, message_id=message_id, text=text)

                    # Update data in DB
                    db_data = {
                           # 'id': departure_id,
                           'time': departure_time,
                           'headsign': departure_headsign,
                           # 'send_status': True,
                           # 'message_id': message_id,
                           # 'chat_id': chat_id,
                           'text': text,
                           'updated': time.time()
                           }
                    db.upsert(self.stop_id, departure_id, db_data)
                    logging.info("Departure " + str(departure_id) + " updated with message details " + str(db_data)) 

    def clean_departures(self):
        logging.info("Cleaning messages and data base for " + str(self.stop_id))
        # Retrieve departures from database
        dead_line = time.time()
        for send_status in [True, False]:
            db_return_based_on_time_response = db.return_based_on_time(self.stop_id, dead_line, send_status)
            
            if len(db_return_based_on_time_response) == 0:
                logging.info("Nothing to delete for bot " + str(self.stop_id) + " and send_status " + str(send_status))

            else:
                for db_item in db_return_based_on_time_response:
                    departure_id = db_item['id']
                    chat_id = db_item['chat_id']
                    message_id = db_item['message_id']

                    # Delete messages
                    rest_response = self.clear_departures_rest.call(chat_id=chat_id, message_id=message_id)
                    logging.info("Response to delete message for " + str(departure_id) + ": " +str(rest_response))

                    # Remove from database
                    db_remove_response = db.remove(self.stop_id, departure_id)
                    logging.info("Response to delete message for " + str(departure_id) + ": " +str(db_remove_response))

        