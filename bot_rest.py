import config
import logging
import requests

class rest:
    def __init__(self, app, service, **kwargs):
        self.service = service
        self.method = config.rest[app][service]['method']
        self.headers = config.rest[app][service]['headers']
        self.url = config.rest[app][service]['url']
        for arg in kwargs:
            if arg in self.url:
                self.url = self.url.replace("{"+arg+"}", kwargs[arg])

    def call(self, body):
        logging.info("Message body is " + str(body))
        if self.method == "POST":
            response = requests.post(self.url, headers=self.headers, json=body).json()
            del body
            return response
        elif self.method == "GET":
            response = requests.get(self.url, headers=self.headers, json=body).json()
            del body
            return response

