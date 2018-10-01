#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from library.common import *
from library.ImageControl import ImageControl
from library.PreseedControl import PreseedControl

class StateControl(object):
    def __init__(self, requester, machine_id):
        if requester is None:
            raise ProvisionerError("Need an initialized Requester instance")
        self.requester = requester
        self.machine_id = machine_id

    def machine_provision(self):
        """ enables netboot on the machine and pxe boots it """
        url = "/api/v1/machine/{}/state".format(self.machine_id)

        data = json.dumps({'state': 'provision'})

        return self.requester.post(url, data)

    def set_machine_parameters(self, preseed_name=None, initrd_desc=None,
                               kernel_desc=None, kernel_opts="",
                               arch=None, subarch=None):
        """ Set parameters on machine specified by machine_id """
        url = "/api/v1/machine/{}".format(self.machine_id)

        image_controller = ImageControl(self.requester)
        preseed_controller = PreseedControl(self.requester,preseed_name)

        if kernel_desc is None or subarch is None:
            raise ProvisionerError("Need at least kernel_desc and subarch with \
                                   an associated bootloader to provision")

        parameters = {}
        if initrd_desc:
            initrd_id = image_controller.get_image(
                    initrd_desc, "Initrd", arch)['id']
            parameters['initrd_id'] = initrd_id

        if kernel_desc:
            kernel_id = image_controller.get_image(kernel_desc,
                                                   "Kernel", arch)['id']
            parameters['kernel_id'] = kernel_id

        if preseed_name:
            preseed_id = preseed_controller.get_preseed()['id']
            parameters['preseed_id'] = preseed_id

        if subarch:
            parameters['subarch'] = subarch

        if kernel_opts:
            parameters['kernel_opts'] = kernel_opts

        parameters['netboot_enabled'] = True

        data = json.dumps(parameters)

        return self.requester.put(url, data)
