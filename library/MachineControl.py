#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import quote

from library.common import *
from library.NetworkControl import NetworkControl
from library.StateControl import StateControl

class MachineControl(object):
    def __init__(self, requester, machine_name):
        self.requester = requester

        try:
            self.machine_id = self._get_id(machine_name)
            self.networkcontrol = NetworkControl(self.requester, self.machine_id)
        except Exception as err:
            raise err

        self.statecontrol = StateControl(self.requester, self.machine_id)

    def _get_id(self, machine_name):
        """ Look up machine by name """
        q = '(= name "{}")'.format(quote(machine_name))
        url = "/api/v1/machine?q={}&show_all=false".format(q)
        try:
            data = self.requester.get(url)
        except Exception as err:
            raise err

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
        try:
            return self.statecontrol.set_machine_parameters(preseed_name, initrd_desc, kernel_desc,
                                                            kernel_opts, arch, subarch)
        except Exception as err:
            raise err

    def provision_machine(self):
        try:
            return self.statecontrol.machine_provision()
        except Exception as err:
            raise err
