import configuration
# import logging
import requests


def resolve_url(service, **kwargs):
    config = configuration.yaml_configurations()
    url = config.rest[service]['url']
    for arg in kwargs:
        if arg in url:
            url = url.replace("{"+arg+"}", kwargs[arg])
    return url

def resolve_body(service, **kwargs):
    config = configuration.yaml_configurations()
    body = config.rest[service]['body']
    for item in body:
        for arg in kwargs:
            if arg in body[item]:
                body[item] = body[item].replace("{"+arg+"}", kwargs[arg])
    print(body)
    return body

def rest(service, **kwargs):
    config = configuration.yaml_configurations()
    method = config.rest[service]['method']
    url = resolve_url(service, **kwargs)
    headers = config.rest[service]['headers']
    body = resolve_body(service, **kwargs)
    if method == "POST":
         return requests.post(url, headers=headers, json=body).json()
    elif method == "GET":
        return requests.get(url, headers=headers, json=body).json()

