#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin
from urllib.parse import quote
from common import ProvisionerError
from common import get_machine_by_name

def machine_provision(url, token, machine_id):
    """ enables netboot on the machine and pxe boots it """
    headers = {'Authorization': token}
    url = urljoin(url, "/api/v1/machine/{}/state".format(machine_id))

    data = json.dumps({'state': 'provision'})

    r = requests.post(url, headers=headers, data=data)

    if r.status_code not in [200, 202]:
        raise ProvisionerError('Error PUTing {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    return r.json()


def set_machine_parameters(url, token, machine_id, initrd_id=None,
                           kernel_id=None, kernel_opts="", preseed_id=None, subarch=None):
    """ Set parameters on machine specified by machine_id """
    headers = {'Authorization': token}
    url = urljoin(url, "/api/v1/machine/{}".format(machine_id))

    parameters = {}
    if initrd_id:
        parameters['initrd_id'] = initrd_id
    if kernel_id:
        parameters['kernel_id'] = kernel_id
    if preseed_id:
        parameters['preseed_id'] = preseed_id
    if subarch:
        parameters['subarch'] = subarch
    if kernel_opts:
        parameters['kernel_opts'] = kernel_opts

    parameters['netboot_enabled'] = True

    data = json.dumps(parameters)

    r = requests.put(url, headers=headers, data=data)

    if r.status_code != 200:
        raise ProvisionerError('Error PUT {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    return r.json()

def get_preseed_by_name(url, token, preseed_name):
    """ Look up preseed by name """
    headers = {'Authorization': token}
    url = urljoin(url, "/api/v1/preseed?show_all=true")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    for preseed in r.json():
        if preseed['name'] == preseed_name:
            del preseed['content'] # we don't need it, and it's really big
            return preseed

    raise ProvisionerError('Error no preseed found with name "{}"'.
            format(preseed_name))

def get_image_by_description(url, token, image_type, description, arch):
    """ Look up image by description """
    headers = {'Authorization': token}
    url = urljoin(url, "/api/v1/image?show_all=true")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    found_image = True
    for image in r.json():
        if (image['description'] == description and
            image['type'] == image_type and
            image['arch'] == arch):
            return image
    msg = "Error finding image of type '{}' and description '{}'".format(
        image_type, description)
    raise ProvisionerError(msg)
