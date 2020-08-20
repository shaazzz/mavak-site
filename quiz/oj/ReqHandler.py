import requests
import pickle
from os import path


class ReqHandler:
    session = requests.session()

    def __init__(self):
        if path.exists("cookies.txt"):
            with open('cookies.txt', 'rb') as f:
                self.session.cookies.update(pickle.load(f))

    def request(self, url, parameters=None, req_type="get"):
        if parameters is None:
            parameters = []
        if req_type == 'get':
            req = requests.get(url, params=parameters)
        elif req_type == 'post':
            req = requests.post(url, params=parameters)
        else:
            raise Exception("invalid request type")
        html_doc = req.text
        return html_doc
