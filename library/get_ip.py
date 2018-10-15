#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from library.common import ProvisionerError
from library.common import *
from urllib.parse import urljoin
from urllib.parse import quote


class IPGetter(object):
    def __init__(self, urlhandler, machine_name, interface_name='eth1'):
        self.urlhandler = urlhandler
        self.interface = interface_name
        self.machine_id = get_machine_by_name(self.urlhandler, machine_name)['id']

    def find_field_by_interface(self, return_field):
        for d in self.get_interfaces():
            if str(d['identifier']) == self.interface:
                return d[return_field]
        raise ProvisionerError("Couldn't find interface %s for machine ID %s" %
                               (self.interface, self.machine_id))

    def get_interfaces(self):
        path = "/api/v1/machine/{}/interface".format(self.machine_id)
        result = self.urlhandler.get(path)
        return result

    def get_ip(self):
        return self.find_field_by_interface('lease_ipv4')

    def get_mac(self):
        return self.find_field_by_interface('mac')

    def get_netmask(self):
        return self.find_field_by_interface('netmaskv4')

