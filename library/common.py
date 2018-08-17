#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from urllib.parse import urljoin
from urllib.parse import quote

class ProvisionerError(Exception):
    def __init__(self, message):
        super(ProvisionerError, self).__init__(message)

class ClientError(Exception):
    def __init__(self, message):
        super(ClientError, self).__init__(message)

class RequesterError(Exception):
    def __init__(self, message, method, url):
        super(RequesterError, self).__init__(message)
        self.method=method
        self.url=url

class RequesterHTTPError(RequesterError):
    def __init__(self,  method, url, status_code, response):
        super(RequesterHTTPError, self).__init__("HTTP ERROR %s on %s request at %s" %
                                                    (str(status_code),
                                                     str(method), str(url)),
                                                 method, url)
        self.status_code=status_code
        self.response=response

class RequesterJSONError(RequesterError):
    def __init__(self, method, url, response):
        super(RequesterJSONError, self).__init__("JSON ERROR on %s request at %s" %
                                                    (str(method), str(url)),
                                                 method, url)
        self.response=response


class Requester(object):
    def __init__(self, mrp_url, mrp_token):
        self.base_url = mrp_url
        self.headers = {'Authorization': mrp_token}

    def get(self, path):
        url = urljoin(self.base_url, path)

        req = requests.get(url, headers=self.headers)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise RequesterHTTPError("GET", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise RequesterJSONError("GET", url, req.text) from jsonerr

        return data

    def put(self, path, data):
        url = urljoin(self.base_url, path)

        req = requests.put(url, headers=self.headers, data=data)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise RequesterHTTPError("PUT", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise RequesterJSONError("PUT", url, req.text) from jsonerr

        return data

    def post(self, path, data, files=None):
        url = urljoin(self.base_url, path)

        if files is not None:
            req = requests.post(url, headers=self.headers, files=files, data=data)
        else:
            req = requests.post(url, headers=self.headers, data=data)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise RequesterHTTPError("POST", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise RequesterJSONError("POST", url, req.text) from jsonerr

        return data

    def delete(self, path):
        url = urljoin(self.base_url, path)

        req = requests.delete(url, headers=self.headers)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise RequesterHTTPError("DELETE", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise RequesterJSONError("DELETE", url, req.text) from jsonerr

        return data

