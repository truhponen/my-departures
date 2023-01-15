import database
import rest
import config
from datetime import datetime
import flatdict
import logging
import time
import utility


class stop_operations:
    def __init__(self, stop_type, stop_id):
        self.stop_type = stop_type
        self.stop_id = stop_id
        self.stop_id_hsl = str('\"'+self.stop_id+'\"').replace("_", ":")
        self.app = 'telegram'
        self.token = config.app['stops'][stop_id]['telegram']['token']
        self.rest_get_departures = rest.rest(self.stop_id, 'hsl', 'get_departures')
        self.rest_get_updates = rest.rest(self.stop_id, str(self.app), 'get_updates', token=self.token)
        self.rest_send_message = rest.rest(self.stop_id, str(self.app), 'send_message', token=self.token)
        self.rest_update_message = rest.rest(self.stop_id, str(self.app), 'update_message', token=self.token)
        self.rest_delete_message = rest.rest(self.stop_id, str(self.app), 'delete_message', token=self.token)
        self.db_departures = database.database('departures_' + str(self.stop_id))
        self.db_subscriptions = database.database('subcriptions_' + str (self.stop_id))
        self.db_update_tracker = database.database('update_tracker' + str (self.stop_id))
    

    def create_subscription(self):
        logging.info("Stop [" + str(self.stop_id) + "] - Get updates")

        update_id = self.db_update_tracker.search_highest('id') + 1
        rest_response = self.rest_get_updates.call(update_id=update_id)  # Get updates

        if rest_response['ok'] == False:
            logging.error("Stop [" + str(self.stop_id) + "] - Response to get updates: " + str(rest_response))

        else:
            logging.info("Stop [" + str(self.stop_id) + "] - Response to get updates: " + str(rest_response))

            if len(rest_response['result']) > 0:

                for item in rest_response['result']:
                    update_id = item['update_id']
                    db_data = {
                               'id': update_id,
                               }
                    self.db_update_tracker.upsert(update_id, db_data)

                    if utility.search_text(rest_response, "/start") > 0:
                        chat_id = item['message']['chat']['id']
                        message_time = item['message']['date']
                        db_data = {
                                'id': chat_id,
                                'update_id': update_id,
                                'time': message_time,
                                'updated': time.time()
                                }

                        if self.db_subscriptions.check_if_exists(chat_id):
                            logging.info("Stop [" + str(self.stop_id) + "] - Chat ID [" + str(chat_id) + "] - Already in database")
                        
                        else:
                            self.db_subscriptions.upsert(chat_id, db_data)  # Update message details to database
                            logging.info("Stop [" + str(self.stop_id) + "] - Chat ID [" + str(chat_id) + "] - Updated database")

                    else:
                        logging.info("Stop [" + str(self.stop_id) + "] - Not \"//start\" message")
            
            else:
                logging.info("Stop [" + str(self.stop_id) + "] - No updates available")


    def delete_subscription(self, chat_id):
        rest_response = self.db_subscriptions.delete(chat_id)
        logging.error("Stop [" + str(self.stop_id) + "] - Response to get updates: " + str(rest_response))


    def get_departures(self):
        logging.info("Stop [" + str(self.stop_id) + "] - Get departures")

        # Request new data set
        rest_response = self.rest_get_departures.call(stop_type=self.stop_type, stop_id_hsl=self.stop_id_hsl)
        new_dataset = flatdict.FlatDict(rest_response, delimiter=".")
        new_dataset = new_dataset['data.'+self.stop_type+'.stoptimesWithoutPatterns']
        logging.info("Stop [" + str(self.stop_id) + "] - HSL data: " + str(new_dataset))

        for departure in new_dataset:  # Define values based on HSL dataset.
            departure_id = str(self.stop_id) + "_" + str(departure['serviceDay'] + departure['scheduledArrival'])
            departure_time = departure['serviceDay'] + departure['realtimeArrival']
            departure_headsign = departure['headsign']

            
            if self.db_departures.check_if_exists(departure_id) == False:  # Check if departure is new and add departure to database.
                logging.info("Stop [" + str(self.stop_id) + "] - Departure " + str(departure_id) + " - Departure is new")
                db_data = {'id': departure_id,
                          'time': departure_time,
                          'headsign': departure_headsign,
                          'send_status': False,
                          'message_id': "",
                          'chat_id': "",
                          'text': "",
                          'updated': time.time()}
            else:
                logging.info("Stop [" + str(self.stop_id) + "] - Departure " + str(departure_id) + " - Departure is old")
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
            self.db_departures.upsert(departure_id, db_data)
            logging.info("Stop [" + str(self.stop_id) + "] - Departure " + str(departure_id) + " - Added / updated departure data")


    def update_messages(self):
        logging.info("Stop [" + str(self.stop_id) + "] - Updating messages")       

        # Retrieve departures from database
        dead_line = time.time() + config.app['time_distance']
        db_response = self.db_departures.search(dead_line, send_status=True)

        if len(db_response) == 0:
            logging.info("Stop [" + str(self.stop_id) + "] - No departures to be updated") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']
                chat_id = ''
                subscriptions = self.db_subscriptions.search(dead_line)
                message_id = departure['message_id']
                text_from_db = departure['text']
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign

                if text == text_from_db:  # Send update only for messages where text has changed
                    logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Message has not changed - Old message [" + str(text_from_db) + "]")
                
                else:
                    logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Message has changed - New message [" + str(text) + "] - Earlier message [" + str(text_from_db) + "]")

                    for subscription in subscriptions:
                        chat_id = subscription['id']
                        rest_response = self.rest_update_message.call(chat_id=chat_id, message_id=message_id, text=text)  # Send message

                        if rest_response['ok'] == False:
                            logging.error("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Response to send message: " + str(rest_response))

                            self.delete_subscription(chat_id)

                        else:
                            logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Response to send message: " + str(rest_response))
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
                            self.db_departures.upsert(departure_id, db_data)  # Update data in DB
                            logging.info("Stop [" + str(self.stop_id) + "] - Departure " + str(departure_id) + " Updated database") 


    def send_messages(self):
        logging.info("Stop [" + str(self.stop_id) + "] - Sending messages")

        dead_line = time.time() + config.app['time_distance']
        db_response = self.db_departures.search(dead_line, send_status=False)  # Retrieve departures from database

        if len(db_response) == 0:
            logging.info("Stop [" + str(self.stop_id) + "] - No new departures to send messages") 

        else:
            for departure in db_response:
                departure_id = departure['id']
                departure_time = departure['time']
                departure_headsign = departure['headsign']
                dead_line = time.time()
                chat_id = ''
                subscriptions = self.db_subscriptions.search(dead_line)
                text = datetime.fromtimestamp(departure_time).strftime("%H:%M") + " - " + departure_headsign  # Form message

                logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Message is " + text)

                for subscription in subscriptions:
                    chat_id = subscription['id']
                    rest_response = self.rest_send_message.call(chat_id=chat_id, text=text)  # Send message
                    
                    if rest_response['ok'] == False:
                        logging.error("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Chat ID [" + str(chat_id) + "] - Response to send message: " + str(rest_response))

                        self.delete_subscription(chat_id)
                    
                    else:
                        logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Chat ID [" + str(chat_id) + "] - Response to send message: " + str(rest_response))

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
                        self.db_departures.upsert(departure_id, db_data)  # Update message details to database
                        logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Chat ID [" + str(chat_id) + "] - Updated database")


    def clean_departures(self):
        logging.info("Stop [" + str(self.stop_id) + "] - Deleting messages and database entries")

        dead_line = time.time()
        db_response = self.db_departures.search(dead_line)  # Retrieve departures from database
        
        if len(db_response) == 0:
            logging.info("Stop [" + str(self.stop_id) + "] - Nothing to delete")

        else:
            for departure in db_response:
                departure_id = departure['id']
                # departure_time = departure['time']
                # departure_headsign = departure['headsign']
                chat_id = departure['chat_id']
                message_id = departure['message_id']
                # text_from_db = departure['text']

                if message_id == "":
                    logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - No message ID. No message sent.")

                else:
                    rest_response = self.rest_delete_message.call(chat_id=chat_id, message_id=message_id)  # Delete messages
                    
                    if rest_response['ok'] == False:
                        logging.error("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Response to delete message: " + str(rest_response))
                    
                    else:
                        logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Response to delete message: " + str(rest_response))

                db_response = self.db_departures.delete(departure_id)  # Remove from database
                logging.info("Stop [" + str(self.stop_id) + "] - Departure [" + str(departure_id) + "] - Response to remove database entry: " + str(db_response))

    