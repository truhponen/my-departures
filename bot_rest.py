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
        self.body_template = config.rest[app][service]['body']

    def form_body(self, **kwargs):
        body = {}
        for item in self.body_template:
            new_value = self.body_template[item]
            for arg in kwargs:
                if arg in new_value:
                    new_value = new_value.replace("{"+arg+"}", kwargs[arg])
            body[item] = new_value

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

