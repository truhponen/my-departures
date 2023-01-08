import bot
import bot_rest
import config
import db
import logging
import time


if config.app['initialize_departures_db']:
    db.drop_tables()
    logging.info("Tables dropped")

my_stops = config.app['stops']
my_bots = []

for stop in my_stops:
    stop = bot.bot_operations(str(stop), config.app['stops'][stop]['stop_type'], stop)
    my_bots.append(stop)
    logging.info("Bot " + str(stop.name) + " created")

logging.info("Starting main program")
while True:
    for item in my_bots:
        item.get_departures()
        item.send_messages()
        item.clean_departures()
    logging.info("Waiting until next updates")
    time.sleep(config.app['update_frequency'])
