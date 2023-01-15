import stop
import config
import logging
import time

my_stops = config.app['stops']
my_bots = []

for item in my_stops:
    item = stop.stop_operations(config.app['stops'][item]['stop_type'], item)
    my_bots.append(item)
    logging.info("[Startup] - Stop [" + str(item.stop_id) + "] created")

logging.info("Starting main program")
while True:
    for item in my_bots:
        logging.info("[Main program] - Stop [" + str(item.stop_id) + "] operations")
        item.create_subscription()
        item.clean_departures()
        item.get_departures()
        item.update_messages()
        item.send_messages()
    logging.info("[Main program] - Waiting until next updates")
    time.sleep(config.app['update_frequency'])
