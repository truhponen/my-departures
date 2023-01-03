from datetime import date
import logging
import yaml


# Serve configurations from yaml-file
class yaml_configurations():

    def __init__(self):
        file_app = open("app/data/config.yaml", "r")
        file_rest = open("app/data/rest_config.yaml", "r")
        self.app = yaml.load(file_app, Loader=yaml.FullLoader)
        self.rest = yaml.load(file_rest, Loader=yaml.FullLoader)
        self.date = date.today()
