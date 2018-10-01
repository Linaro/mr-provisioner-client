#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import ipaddress

from library.common import *
from urllib.parse import quote


class NetworkControl(object):
    def __init__(self, requester, machine_id, interface_name='eth1'):
        if requester is None:
            raise ProvisionerError("Need an initialized Requester instance")
        self.requester = requester
        self.machine_id = machine_id
        self.machine_ip = ''
        self.interface = self.get_interface(interface_name)

    def get(self, command):
        if command == 'getip':
            return self.get_ip()
        elif command == 'getmac':
            return self.get_mac()
        elif command == 'getnetmask':
            return self.get_netmask()
        elif command == 'getnetwork':
            return self.get_network()
        elif command == 'getall':
            return self.get_all()
        else:
            raise ProvisionerError("Unknown Command : %s" % command)

    def get_interface(self, interface_name):
        url = "/api/v1/machine/{}/interface".format(self.machine_id)
        interfaces = self.requester.get(url)

        # interfaces contains a dictionary per machine interface registered in
        # MrP, with its 'identifier' being its 'name'.
        for interface in interfaces:
            if str(interface['identifier']) == interface_name:
                return interface

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

