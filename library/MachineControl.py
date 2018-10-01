#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import quote

from library.common import *
from library.NetworkControl import NetworkControl
from library.StateControl import StateControl

class MachineControl(object):
    def __init__(self, requester, machine_name):
        self.requester = requester
        self.machine_id = self._get_id(machine_name)
        self.networkcontrol = NetworkControl(self.requester, self.machine_id)
        self.statecontrol = StateControl(self.requester, self.machine_id)

    def _get_id(self, machine_name):
        """ Look up machine by name """
        q = '(= name "{}")'.format(quote(machine_name))
        url = "/api/v1/machine?q={}&show_all=false".format(q)

        data = self.requester.get(url)

        return data[0]['id']

    def get_network_info(self, command, interface_name):
        if command == 'getip':
            return self.networkcontrol.get_ip()
        elif command == 'getmac':
            return self.networkcontrol.get_mac()
        elif command == 'getnetmask':
            return self.networkcontrol.get_netmask()
        elif command == 'getnetwork':
            return self.networkcontrol.get_network()
        elif command == 'getall':
            return self.networkcontrol.get_all()
        else:
            raise LookupError("Unknown Command : %s" % command)

    def set_machine_provisioning(self, preseed_name, initrd_desc, kernel_desc,
                                 kernel_opts, arch, subarch):
        return self.statecontrol.set_machine_parameters(preseed_name, initrd_desc, kernel_desc,
                                                            kernel_opts, arch, subarch)

    def provision_machine(self):
        return self.statecontrol.machine_provision()
