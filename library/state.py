#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin
from urllib.parse import quote
from library.common import ProvisionerError
from library.common import get_machine_by_name
from library.image import ImageUploader
from library.preseed import PreseedUploader


class MachineProvisioner(object):
    def __init__(self, mrp_url, mrp_token, machine_name):
        self.mrp_url = mrp_url
        self.mrp_token = mrp_token
        self.machine_name = machine_name
        self.machine_id = None
        self.headers = {'Authorization': self.mrp_token}
        self.validate_name()

    def validate_name(self):
        try:
            machine = get_machine_by_name(
                self.mrp_token, self.mrp_url, self.machine_name)
            self.machine_id = machine['id']
        except ProvisionerError as e:
            print(e)

    def machine_provision(self):
        """ enables netboot on the machine and pxe boots it """
        url = urljoin(
            self.mrp_url, "/api/v1/machine/{}/state".format(self.machine_id))

        data = json.dumps({'state': 'provision'})

        r = requests.post(url, headers=self.headers, data=data)

        if r.status_code not in [200, 202]:
            raise ProvisionerError('Error PUTing {}, HTTP {} {}'.format(url,
                                                                        r.status_code, r.reason))
        return r.json()

    def set_machine_parameters(self, preseed_name, initrd_desc=None,
                               kernel_desc=None, kernel_opts="",
                               arch=None, subarch=None):
        """ Set parameters on machine specified by machine_id """
        url = urljoin(
            self.mrp_url, "/api/v1/machine/{}".format(self.machine_id))

        image_controller = ImageUploader(self.mrp_url, self.mrp_token)
        preseed_controller = PreseedUploader(self.mrp_url, self.mrp_token,
                                             preseed_name)

        parameters = {}
        if initrd_desc:
            try:
                initrd_id = image_controller.getImageID(
                    initrd_desc, "Initrd", arch)
                parameters['initrd_id'] = initrd_id
            except ProvisionerError as e:
                print(e)
                raise

        if kernel_desc:
            try:
                kernel_id = image_controller.getImageID(kernel_desc,
                                                        "Kernel", arch)
                parameters['kernel_id'] = kernel_id
            except ProvisionerError as e:
                print(e)
                raise
        if preseed_name:
            try:
                preseed_id = preseed_controller.getPreseedID()
                parameters['preseed_id'] = preseed_id
            except ProvisionerError as e:
                print(e)
                raise
        if subarch:
            parameters['subarch'] = subarch
        if kernel_opts:
            parameters['kernel_opts'] = kernel_opts

        parameters['netboot_enabled'] = True

        data = json.dumps(parameters)

        r = requests.put(url, headers=self.headers, data=data)

        if r.status_code != 200:
            raise ProvisionerError('Error PUT {}, HTTP {} {}'.format(url,
                                                                     r.status_code, r.reason))
        return r.json()
