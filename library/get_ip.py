#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from library.common import ProvisionerError
from library.common import *
from urllib.parse import urljoin
from urllib.parse import quote


class IPGetter(object):
    def __init__(self, requester, machine_name, interface_name='eth1'):
        self.requester = requester
        self.interface = interface_name
        self.machine_id = get_machine_by_name(
            self.requester, machine_name)['id']
        self.machine_ip = ''

    def get_interfaces(self):
        path = "/api/v1/machine/{}/interface".format(self.machine_id)
        try:
            result = self.requester.get(path)
        except Exception as err:
            raise err

        return result

    def get_ip(self):
        try:
            interfaces = self.get_interfaces()
        except ProvisionerError as err:
            raise err

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                return i['lease_ipv4']

        raise ProvisionerError("Couldn't find interface %s for machine ID %s" %
                               (self.interface, self.machine_id))

    def get_mac(self):
        try:
            interfaces = self.get_interfaces()
        except ProvisionerError as err:
            raise err

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                return i['mac']

        raise ProvisionerError("Couldn't find interface %s for machine ID %s" %
                               (self.interface, self.machine_id))

    def get_netmask(self):
        try:
            interfaces = self.get_interfaces()
        except ProvisionerError as err:
            raise err

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                return i['netmaskv4']

        raise ProvisionerError("Couldn't find interface %s for machine ID %s" %
                               (self.interface, self.machine_id))
