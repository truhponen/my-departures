import config
import logging
import requests

class rest:
    def __init__(self, service, **kwargs):
        self.service = service
        self.method = config.rest[service]['method']
        self.headers = config.rest[service]['headers']
        self.url = config.rest[service]['url']
        for arg in kwargs:
            if arg in self.url:
                self.url = self.url.replace("{"+arg+"}", kwargs[arg])

    def call(self, body):
        if self.method == "POST":
            logging.info("Body for " + str(self.service) + " is " + str(body))
            response = requests.post(self.url, headers=self.headers, json=body).json()
            del body
            return response
        elif self.method == "GET":
            logging.info("Body is " + str(body))
            response = requests.get(self.url, headers=self.headers, json=body).json()
            del body
            return response

