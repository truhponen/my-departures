import bot_operations
import configuration
import db
import logging
import time
# import updates_from_bot


# Load configuration
config = configuration.yaml_configurations()

logging.basicConfig(filename='./app/data/logs/' + str(config.date) + '.log', level=(config.app['logging_level']))

if config.app['initialize_departures_db']:
    db.drop_tables()
    logging.info("Tables dropped")

my_bots = []

logging.info("Adding stations to bot list")
for station in config.app['station']:
    station = bot_operations.departures_to_bot(station, 'station', station)
    my_bots.append(station)
    logging.info("Bot " + str(station.name) + " created")

logging.info("Adding stops to bot list")
for stop in config.app['stop']:
    my_bots.append(stop)
    logging.info("Bot " + str(stop.name) + " added to 'my_bots'-list")

while True:
    logging.info("Starting main program")
    for item in my_bots:
        item.update_departures()
    logging.info("Waiting until next updates")
    time.sleep(config.app['update_frequency'])
