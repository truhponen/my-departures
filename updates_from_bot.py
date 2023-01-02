import logging
import configuration
import calls


def get():
    config = configuration.yaml_configurations()
    service = str(config['app'].lower()) + "_get_updates"
    response = calls.rest(service)
    print(response)
    # https://api.telegram.org/bot5889356316:AAHWfP6uXPiLMG1hurV9RxYwJ87LjRHGUvE/getUpdates

get()
