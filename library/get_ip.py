#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from common import ProvisionerError
from urllib.parse import urljoin
from urllib.parse import quote

class IPGetter(object):
    def __init__(self, mrpurl, mrptoken, machine_id, interface_name =
                 'eth1'):
        self.mrp_url = mrpurl
        self.mrp_token = mrptoken
        self.interface = interface_name
        self.machine_id = machine_id
        self.machine_ip = ''

    def get_interfaces(self):
        headers = {'Authorization': self.mrp_token}
        url = urljoin(self.mrp_url,
                      "/api/v1/machine/{}/interface".format(self.machine_id))
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(self.mrp_url, r.status_code,
                                                         r.reason))
        if len(r.json()) == 0:
            raise ProvisionerError('Error no machine with id "{}"'.format(self.machine_id))

        return r.json()

    def get_ip(self):
        try:
            interfaces = self.get_interfaces()
        except ProvisionerError as e:
            print('Could not fetch interface for machine : "{}"'.format(e))
            return 'FAILURE'

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                    return i['lease_ipv4']

