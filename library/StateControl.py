#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from library.common import *
from library.ImageControl import ImageControl
from library.PreseedControl import PreseedControl

class StateControl(object):
    def __init__(self, requester, machine_id):
        self.requester = requester
        self.machine_id = machine_id

    def machine_provision(self):
        """ enables netboot on the machine and pxe boots it """
        url = "/api/v1/machine/{}/state".format(self.machine_id)

        data = json.dumps({'state': 'provision'})

        try:
            return self.requester.post(url, data)
        except Exception as err:
            raise err

    def set_machine_parameters(self, preseed_name=None, initrd_desc=None,
                               kernel_desc=None, kernel_opts="",
                               arch=None, subarch=None):
        """ Set parameters on machine specified by machine_id """
        url = "/api/v1/machine/{}".format(self.machine_id)

        image_controller = ImageControl(self.requester)
        preseed_controller = PreseedControl(self.requester,preseed_name)

        parameters = {}
        if initrd_desc:
            try:
                initrd_id = image_controller.get_image_id(
                    initrd_desc, "Initrd", arch)
                parameters['initrd_id'] = initrd_id
            except Exception as err:
               raise err

        if kernel_desc:
            try:
                kernel_id = image_controller.get_image_id(kernel_desc,
                                                        "Kernel", arch)
                parameters['kernel_id'] = kernel_id
            except Exception as err:
               raise err

        if preseed_name:
            try:
                preseed_id = preseed_controller.get_preseed_id()
                parameters['preseed_id'] = preseed_id
            except Exception as err:
               raise err

        if subarch:
            parameters['subarch'] = subarch

        if kernel_opts:
            parameters['kernel_opts'] = kernel_opts

        parameters['netboot_enabled'] = True

        data = json.dumps(parameters)

        try:
            return self.requester.put(url, data)
        except Exception as err:
            raise err
