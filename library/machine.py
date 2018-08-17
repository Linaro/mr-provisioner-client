#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from urllib.parse import urljoin
from urllib.parse import quote

from library.common import *
from library.network import NetworkControl
from library.state import StateControl

class MachineControl(object):
    def __init__(self, requester, machine_name):
        self.requester = requester
        self.log = logging.getLogger(__name__)

        try:
            self.machine_id = self._get_id(machine_name)
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

        self.networkcontrol = NetworkControl(self.requester, self.machine_id)
        self.statecontrol = StateControl(self.requester, self.machine_id)

    def _get_id(self, machine_name):
        """ Look up machine by name """
        q = '(= name "{}")'.format(quote(machine_name))
        url = "/api/v1/machine?q={}&show_all=false".format(q)
        try:
            data = self.requester.get(url)
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

        self.log.debug('Machine ID: %s' % data[0]['id'])
        return data[0]['id']

    def get_network_info(self, command, interface_name):
        if command == 'ip':
            return self.networkcontrol.get_ip()
        elif command == 'mac':
            return self.networkcontrol.get_mac()
        elif command == 'netmask':
            return self.networkcontrol.get_netmask()
        else:
            self.log.fatal('UNKNOWN COMMAND for get_network_info : %s' %
                           command)
            exit(2)

    def set_machine_provisioning(self, preseed_name, initrd_desc, kernel_desc,
                                 kernel_opts, arch, subarch):
        self.statecontrol.set_machine_parameters(preseed_name, initrd_desc, kernel_desc,
                                 kernel_opts, arch, subarch)

    def provision_machine(self):
        self.statecontrol.machine_provision()
