import config
import logging
import requests

class rest:
    def __init__(self, stop_id, app, service, **kwargs):
        self.stop_id = stop_id
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
                if str(arg) in str(new_value):
                    new_value = str(new_value).replace("{"+arg+"}", str(kwargs[arg]))
            body[item] = new_value
        return body

    def call(self, **kwargs):
        body = self.form_body(**kwargs)
        logging.info("Stop [" + str(self.stop_id) + "] - Message body: " + str(body))
        if self.method == "POST":
            response = requests.post(self.url, headers=self.headers, json=body).json()
            return response
        elif self.method == "GET":
            response = requests.get(self.url, headers=self.headers, json=body).json()
            return response

