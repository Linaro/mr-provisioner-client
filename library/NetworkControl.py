#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import ipaddress

from library.common import *
from urllib.parse import quote


class NetworkControl(object):
    def __init__(self, requester, machine_id, interface_name='eth1'):
        self.log = logging.getLogger(__name__)
        self.requester = requester
        self.machine_id = machine_id
        self.interface_name = interface_name
        self.machine_ip = ''
        try:
            self.interface = self.get_interface()
        except Exception as err:
            raise err

    def get_interface(self):
        url = "/api/v1/machine/{}/interface".format(self.machine_id)
        try:
            interfaces = self.requester.get(url)
        except Exception as err:
            raise err

        for i in interfaces:
            if str(i['identifier']) == self.interface_name:
                return i

    def get_ip(self):
        return self.interface['lease_ipv4']

    def get_mac(self):
        return self.interface['mac']

    def get_netmask(self):
        if self.interface['netmaskv4'] is None:
            return 'Network Not Configured in MrP'

        return self.interface['netmaskv4']

    def get_network(self):
        if self.get_netmask() == 'Network Not Configured in MrP':
            return 'Network Not Configured in MrP'
        return str(ipaddress.ip_network(str(self.get_ip()) + '/' +
                                        str(self.get_netmask())))

    def get_all(self):
        all = "IP: " + str(self.get_ip()) + '\n'
        all += "MAC: " + str(self.get_mac()) + '\n'
        all += "Network: " + str(self.get_network()) + '\n'
        return all

