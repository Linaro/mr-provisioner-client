#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import quote

from library.common import *
from library.NetworkControl import NetworkControl
from library.StateControl import StateControl

class MachineControl(object):
    def __init__(self, requester, machine_name, interface_name='eth1'):
        if requester is None:
            raise ProvisionerError("Need an initialized instance of Requester")
        self.requester = requester
        self.config = self._get_machine(machine_name)
        self.machine_id = self.config[0]['id']
        self.networkcontrol = NetworkControl(self.requester, self.machine_id,
                                             interface_name)
        self.statecontrol = StateControl(self.requester, self.machine_id)

    def _get_machine(self, machine_name):
        """ Look up machine by name """
        q = '(= name "{}")'.format(quote(machine_name))
        url = "/api/v1/machine?q={}&show_all=false".format(q)

        data = self.requester.get(url)

        if len(data) <= 0 or type(data[0]) is not dict or type(data[0]['id']) is not int:
            raise TypeError("Failed to fetch ID for %s, data corrupted : '%s'" %
                            (machine_name, data))

        return data

    def get_network_info(self):
        return self.networkcontrol.get_all()

    def set_machine_provisioning(self, preseed_name, initrd_desc, kernel_desc,
                                 kernel_opts, arch, subarch):
        return self.statecontrol.set_machine_parameters(preseed_name, initrd_desc, kernel_desc,
                                                            kernel_opts, arch, subarch)

    def provision_machine(self):
        return self.statecontrol.machine_provision()
