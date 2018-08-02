#!/usr/bin/env python3

import requests
import json
from urllib.parse import urljoin
from urllib.parse import quote

class ProvisionerError(Exception):
    def __init__(self, message):
        super(ProvisionerError, self).__init__(message)

def get_machine_by_name(mrp_token, mrp_url, machine_name):
    """ Look up machine by name """
    headers = {'Authorization': mrp_token}
    q = '(= name "{}")'.format(quote(machine_name))
    url = urljoin(mrp_url, "/api/v1/machine?q={}&show_all=false".format(q))
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(mrp_url,
                         r.status_code, r.reason))
    if len(r.json()) == 0:
       raise ProvisionerError('Error no assigned machine found with name "{}"'.
                    format(machine_name))
    if len(r.json()) > 1:
       raise ProvisionerError('Error more than one machine found with name "{}", {}'.
                    format(machine_name, r.json()))
    return r.json()[0]
