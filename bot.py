import db
import calls
import configuration
from datetime import datetime
import flatdict
import logging
import time


# Load configuration
config = configuration.yaml_configurations()

class bot_operations:
    def __init__(self, name, stop_type, stop_id):
        self.name = name
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = config.app[stop_type][stop_id]['app'].lower()
        self.app_token = config.app[stop_type][stop_id]['token']

    def get_departures(self):
        while True:
            
            logging.info("Updating bot " + str(self.stop_id))
            # Retrieve HSL dataset and flatten it.
            service = 'hsl'
            new_dataset = calls.rest(service, stop_type=self.stop_type, stop_id=self.stop_id_hsl)
            new_dataset = flatdict.FlatDict(new_dataset, delimiter=".")
            new_dataset = new_dataset['data.'+self.stop_type+'.stoptimesWithoutPatterns']
            logging.info("HSL data for " + str(self.stop_id) + " retrieved")

            # Define values based on HSL dataset.
            for departure in new_dataset:
                departure_id = departure['serviceDay'] + departure['scheduledArrival']
                departure_time = departure['serviceDay'] + departure['realtimeArrival']
                departure_headsign = departure['headsign']

                # Check if departure is new...
                if db.if_value_exists(self.stop_id, departure_id) == False:
                    logging.info("HSL data for departure " + str(departure_id) + " is new")

                    # ... and add departure to database.
                    departure_data = {
                        'id': departure_id,
                        'time': departure_time,
                        'headsign': departure_headsign}
                    db.insert(self.stop_id, departure_data)
                    logging.info("Stored departure " + str(departure_data))
                    
        time.sleep(config.app['update_frequency'])

    def send_messages(self):
        while True:
            # Retrieve departures
            # FROM table self.stop_id
            # departures WHERE
            # time.time < departure_time < time.time + [departure_time]
            # and result.message_id is null
            # logging.info("HSL data for departure " + str(departure_id) + " is new. Sending message.")

            # for departure in db_response:
                # Send messages
                # service = str(self.app) + "_send_message_" + self.stop_id
                # message = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign
                # calls.rest(service, app_token=self.app_token, message=message)
                # logging.info("Message " + str(self.message + " for departure " + str(departure_id) + " sent"))

                # Update database key with {message_id: result.message_id and chat_id: result.chat.id
                # departure_data = {'message_id': message_id,
                #                   'chat_id': chat_id}
                # db.update(self.stop_id, departure_data)

            time.sleep(60)                

    def clean_departures(self):
        while True:
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

            time.sleep(60)
