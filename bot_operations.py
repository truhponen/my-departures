import db
import calls
import configuration
from datetime import datetime
import flatdict
import logging
import time


# Load configuration
config = configuration.yaml_configurations()

class departures_to_bot:
    def __init__(self, name, stop_type, stop_id):
        self.name = name
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = config.app[stop_type][stop_id]['app'].lower()
        self.app_token = config.app[stop_type][stop_id]['token']

    def update_departures(self):
        logging.info("Updating bot " + str(self.stop_id))
        # Retrieve HSL dataset and flatten it.
        self.service = 'hsl'
        self.new_dataset = calls.rest(self.service, stop_type=self.stop_type, stop_id=self.stop_id_hsl)
        self.new_dataset = flatdict.FlatDict(self.new_dataset, delimiter=".")
        self.new_dataset = self.new_dataset['data.'+self.stop_type+'.stoptimesWithoutPatterns']
        logging.info("HSL data for " + str(self.stop_id) + " retrieved")

        # Define values based on HSL dataset.
        for self.departure in self.new_dataset:
            self.departure_id = self.departure['serviceDay'] + self.departure['scheduledArrival']
            self.departure_time = self.departure['serviceDay'] + self.departure['realtimeArrival']
            self.departure_headsign = self.departure['headsign']

            # Check if departure is new...
            if db.if_value_exists(self.stop_id, self.departure_id) == False:
                logging.info("HSL data for departure " + str(self.departure_id) + " is new")

                # ... send message
                self.service = str(self.app) + "_send_message_" + self.stop_id
                self.message = datetime.fromtimestamp(self.departure_time).strftime("%H:%M") + " - " + self.departure_headsign
                calls.rest(self.service, app_token=self.app_token, message=self.message)
                logging.info("Message " + str(self.message + " for departure " + str(self.departure_id) + " sent"))

                # ... and add departure to database.
                self.departure_data = {
                    'id': self.departure_id,
                    'time': self.departure_time,
                    'headsign':self.departure_headsign}
                db.insert(self.stop_id, self.departure_data)
                logging.info("Stored data " + str(self.departure_data))

        # Remove past departures from database table
        db.remove_based_on_time(self.stop_id, time.time())

        return
