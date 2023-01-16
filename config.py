from datetime import date
import logging
import os
import yaml


app_dir = "." + str(os.environ['APP_DIR'])
# app_dir = "."
file_app = open(app_dir + "/data/config.yaml", "r")
file_rest = open(app_dir + "/data/rest_config.yaml", "r")
app = yaml.load(file_app, Loader=yaml.FullLoader)
rest = yaml.load(file_rest, Loader=yaml.FullLoader)
date = date.today()
db = app_dir + "/data/departures.json"

logging.basicConfig(filename=app_dir + '/data/logs/' + str(date) + '.log', level=(app['logging_level']))
