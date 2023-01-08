import db
import calls
import config
from datetime import datetime
import flatdict
import logging
import time


# Load configuration
# config = configuration.yaml_configurations()

class bot_operations:
    def __init__(self, name, stop_type, stop_id):
        self.name = name
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = config.app[stop_type][stop_id]['app'].lower()
        self.app_token = config.app[stop_type][stop_id]['token']
        self.get_departures_rest = calls.rest('hsl')
        self.send_message_rest = calls.rest(str(self.app) + "_send_message_" + self.stop_id, app_token=self.app_token)
        self.clear_departures_rest = calls.rest(str(self.app) + "_delete_message_" + self.stop_id, app_token=self.app_token)

    def get_departures(self):
        
        logging.info("Updating bot " + str(self.stop_id))
        # Retrieve HSL dataset and flatten it.
        body = config.rest[self.get_departures_rest.service]['body']
        ids = {'stop_type': self.stop_type, 'stop_id_hsl': self.stop_id_hsl}
        for item in body:
            for id in ids:
                if id in body[item]:
                    body[item] = body[item].replace("{" + str(id) +"}", str(ids[id]))
        new_dataset = self.get_departures_rest.call(body)
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
                departure_data = {
                    'id': departure_id,
                    'time': departure_time,
                    'headsign': departure_headsign,
                    'send_status': False,
                    'message_id': "",
                    'chat_id': ""}
                db.upsert(self.stop_id, departure_id, departure_data)
                logging.info("Stored departure " + str(departure_data))

            else:
                logging.info("HSL data for departure " + str(departure_id) + " is old")
                departure_data = {
                    'id': departure_id,
                    'time': departure_time}
                db.upsert(self.stop_id, departure_id, departure_data)
                logging.info("Stored departure " + str(departure_data))

    def send_messages(self):
        
        logging.info("Send message for " + str(self.stop_id))
        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = db.return_based_on_time(self.stop_id, dead_line, False)

        if len(db_response) == 0:
            logging.info("No new dedpartures to send messages") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']

                # Send messages
                message = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                logging.info("Message is " + message)
                body = {'chat_id': config.rest[self.send_message_rest.service]['body']['chat_id'] ,'text': message}
                rest_response = self.send_message_rest.call(body)
                
                # Update message details to database
                message_ids = rest_response['result']['message_id']
                chat_ids = rest_response['result']['chat']['id']

                message_data = {'send_status': True,
                                'message_id': message_ids,
                                'chat_id': chat_ids}
                db.upsert(self.stop_id, departure_id, message_data)
                logging.info("Departure " + str(departure_id) + " updated with message details " + str(message_data))          


    def clean_departures(self):

        logging.info("Cleaning messages and data base " + str(self.stop_id))
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

                    # Remove messages
                    body = {'chat_id': chat_id, 'message_id': message_id}
                    rest_response = self.clear_departures_rest.call(body)
                    logging.info("Response to delete message for " + str(departure_id) + ": " +str(rest_response))

                    # Remove from database
                    db_remove_response = db.remove(self.stop_id, departure_id)
                    logging.info("Response to delete message for " + str(departure_id) + ": " +str(db_remove_response))

        # Retrieve departures
        # FROM table self.stop_id
        # departures WHERE
        # self.stop_id
        # departure_time < time.time

        # If messages has message_id
        # service = str(self.app) + "_remove_message_" + self.stop_id
        # calls.rest(service, app_token=self.app_token, chat_id, message_id)

        # Remove past departures from database table
        # db.remove_based_on_time(self.stop_id, time.time())
        