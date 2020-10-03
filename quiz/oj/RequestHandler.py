import pickle
from os import path

import requests


class RequestHandler:
    session = requests.session()

    def __init__(self):
        if path.exists("cookies.txt"):
            with open('cookies.txt', 'rb') as f:
                self.session.cookies.update(pickle.load(f))

    def clear_cookies(self):
        self.session.cookies.clear()
        with open('cookies.txt', 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def request(self, url, parameters=None, req_type="post"):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'
        }
        if parameters is None:
            parameters = []
        if req_type == 'get':
            req = requests.get(url, params=parameters, headers=headers, cookies=self.session.cookies)
        elif req_type == 'post':
            req = requests.post(url, params=parameters, headers=headers, cookies=self.session.cookies)
        else:
            raise Exception("invalid request type")
        self.session.cookies.update(requests.utils.dict_from_cookiejar(req.cookies))
        html_doc = req.text
        with open('cookies.txt', 'wb') as f:
            pickle.dump(self.session.cookies, f)
        return html_doc
