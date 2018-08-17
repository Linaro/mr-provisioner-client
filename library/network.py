#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from library.common import *
from urllib.parse import quote


class NetworkControl(object):
    def __init__(self, requester, machine_id, interface_name='eth1'):
        self.log = logging.getLogger(__name__)
        self.requester = requester
        self.machine_id = machine_id
        self.interface_name = interface_name
        self.machine_ip = ''

    def set_interface_name(self, interface_name):
        self.interface_name = interface_name

    def get_interface(self):
        url = "/api/v1/machine/{}/interface".format(self.machine_id)
        try:
            interfaces = self.requester.get(url)
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

        for i in interfaces:
            if str(i['identifier']) == self.interface_name:
                return i

    def get_ip(self):
        interface = self.get_interface()
        return interface['lease_ipv4']

    def get_mac(self):
        interface = self.get_interface()
        return interface['mac']

    def get_netmask(self):
        interface = self.get_interface()
        return interface['netmaskv4']
