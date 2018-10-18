#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ipaddress

from library.common import *
from urllib.parse import quote

class NetworkControl(object):
    def __init__(self, urlhandler, machine_id, interface_name):
        self.urlhandler = urlhandler
        self.machine_id = machine_id
        self.interface = self.get_interface(interface_name)

    def get_interface(self, interface_name):
        url = "/api/v1/machine/{}/interface".format(self.machine_id)
        interfaces = self.urlhandler.get(url)

        if not interfaces:
            raise ProvisionerError("No interfaces for machine id %s" %
                                   self.machine_id)

        for i in interfaces:
            if 'identifier' in i and str(i['identifier']) == interface_name:
                return i

        raise ProvisionerError("Couldn't find interface %s for machine ID %s" %
                               (interface_name, self.machine_id))

    def get_ip(self):
        if 'lease_ipv4' in self.interface:
            return self.interface['lease_ipv4']
        return ''

    def get_mac(self):
        if 'mac' in self.interface:
            return self.interface['mac']
        return ''

    def get_netmask(self):
        if 'netmaskv4' in self.interface:
            return self.interface['netmaskv4']
        return ''
