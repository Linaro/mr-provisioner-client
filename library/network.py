#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from library.common import ProvisionerError
from library.common import get_machine_by_name
from urllib.parse import urljoin
from urllib.parse import quote


class IPGetter(object):
    def __init__(self, mrpurl, mrptoken, machine_name, interface_name='eth1'):
        self.mrp_url = mrpurl
        self.mrp_token = mrptoken
        self.interface = interface_name
        self.machine_id = get_machine_by_name(
            self.mrp_token, self.mrp_url, machine_name)['id']
        self.machine_ip = ''
        self.headers = {'Authorization': self.mrp_token}

    def get_interface(self):
        url = urljoin(self.mrp_url,
                      "/api/v1/machine/{}/interface".format(self.machine_id))
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {} {}, HTTP {} {}'.format(
                url, self.interface, r.status_code, r.reason))

        if len(r.json()) == 0:
            raise ProvisionerError(
                'Error no machine with id "{}"'.format(self.machine_id))

        interfaces = r.json()

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                return i

    def get_ip(self):
        try:
            interface = self.get_interface()
        except ProvisionerError as e:
            print('Could not fetch interface for machine : "{}"'.format(e))
            return 'FAILURE'

        return interface['lease_ipv4']

    def get_mac(self):
        try:
            interface = self.get_interface()
        except ProvisionerError as e:
            print('Could not fetch interface for machine : "{}"'.format(e))
            return 'FAILURE'

        return interface['mac']

    def get_netmask(self):
        try:
            interface = self.get_interface()
        except ProvisionerError as e:
            print('Could not fetch interface for machine : "{}"'.format(e))
            return 'FAILURE'

        return interface['netmaskv4']
