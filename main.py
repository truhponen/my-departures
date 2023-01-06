import bot
import configuration
import db
import logging
import os
import time


# Load configuration
config = configuration.yaml_configurations()

# app_dir = os.environ['APP_DIR']
app_dir = "."
logging.basicConfig(filename=app_dir + '/data/logs/' + str(config.date) + '.log', level=(config.app['logging_level']))

if config.app['initialize_departures_db']:
    db.drop_tables()
    logging.info("Tables dropped")

my_bots = []

logging.info("Adding stations to bot list")
if len(config.app['station']) == 0:
    logging.info("No stations defined")
else:
    for station in config.app['station']:
        station = bot.bot_operations(station, 'station', station)
        my_bots.append(station)
        logging.info("Bot " + str(station.name) + " created")

logging.info("Adding stops to bot list")
if len(config.app['stop']) == 0:
    logging.info("No stops defined")
else:
    for stop in config.app['stop']:
        my_bots.append(stop)
        logging.info("Bot " + str(stop.name) + " added to 'my_bots'-list")

logging.info("Starting main program")
while True:
    for item in my_bots:
        item.get_departures()
        item.send_messages()
        item.clean_departures()
    logging.info("Waiting until next updates")
    time.sleep(config.app['update_frequency'])
