#!/usr/bin/env python3

import requests
import json
from urllib.parse import urljoin
from urllib.parse import quote

# TODO: This needs a more standard name (static method)
# Or we need to make sure the IPGetter object is easy to use
def get_machine_id(urlhandler, machine_name):
    """ Look up machine by name """
    q = '(= name "{}")'.format(quote(machine_name))
    path = "/api/v1/machine?q={}&show_all=false".format(q)
    result = urlhandler.get(path)
    return result[0]['id']

class ProvisionerError(Exception):
    def __init__(self, message):
        super(ProvisionerError, self).__init__(message)

class ClientError(Exception):
    def __init__(self, message):
        super(ClientError, self).__init__(message)

class URLhandlerError(Exception):
    def __init__(self, message, method, url):
        super(URLhandlerError, self).__init__(message)
        self.method = method
        self.url = url

class URLhandlerHTTPError(URLhandlerError):
    def __init__(self, method, url, status_code, response):
        super(URLhandlerHTTPError, self).__init__("HTTP ERROR %s on %s request at %s" %
                                                 (str(status_code), str(method), str(url)),
                                                 method, url)
        self.status_code = status_code
        self.response = response

class URLhandlerJSONError(URLhandlerError):
    def __init__(self, method, url, response):
        super(URLhandlerJSONError, self).__init__("JSON ERROR on %s request at %s" %
                                                 (str(method), str(url)), method, url)
        self.response = response


class URLhandler(object):
    def __init__(self, mrp_url, mrp_token):
        try:
            self.base_url = mrp_url
            self.headers = {'Authorization': mrp_token}
            self.get("/api/v1/machine?show_all=false")
        except Exception as err:
            raise ClientError("Invalid URL or token for MrP") from err

    def get(self, path):
        url = urljoin(self.base_url, path)

        req = requests.get(url, headers=self.headers)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise URLhandlerHTTPError("GET", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise URLhandlerJSONError("GET", url, req.text) from jsonerr

        return data

    def put(self, path, data):
        url = urljoin(self.base_url, path)

        req = requests.put(url, headers=self.headers, data=data)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise URLhandlerHTTPError("PUT", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise URLhandlerJSONError("PUT", url, req.text) from jsonerr

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
            raise URLhandlerHTTPError("POST", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise URLhandlerJSONError("POST", url, req.text) from jsonerr

        return data

    def delete(self, path):
        url = urljoin(self.base_url, path)

        req = requests.delete(url, headers=self.headers)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as herr:
            raise URLhandlerHTTPError("DELETE", url, req.status_code, req.text) from herr

        try:
            data = req.json()
        except ValueError as jsonerr:
            raise URLhandlerJSONError("DELETE", url, req.text) from jsonerr

        return data
