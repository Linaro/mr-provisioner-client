#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin
from urllib.parse import quote

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mr-provisioner-machine-provision

short_description: Provision a machine in Mr. Provisioner.

description:
    Implemented:
        - Set machine's initrd, kernel
        - Provision machine
        - Wait for machine to come online
    Not implemented:
        -
        -

options:
    machine_name:
        description: Machine name
        required: true
    kernel_description:
        description: kernel description
        required: true
    initrd_description:
        description: initrd description
        required: true
    arch:
        description: Image architecture. e.g. arm64, x86_64
        required: true
    subarch:
        description: Machine subarchitecture. e.g. efi, bios
        required: true
    preseed_name:
        description: name of preseed to use.
        required: true
    kernel_options:
        description: kernel boot command line
        required: false
    url:
        description: url to provisioner instance in the form of http://192.168.0.3:5000/
        required: true
    token:
        description: Mr. Provisioner auth token
        required: true

author:
    - Dan Rue <dan.rue@linaro.org>
'''

EXAMPLES = '''

'''

RETURN = '''

'''

# TODO: This needs to be common to all modules
class ProvisionerError(Exception):
    def __init__(self, message):
        super(ProvisionerError, self).__init__(message)


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

def get_machine_by_name(url, token, machine_name):
    """ Look up machine by name """
    headers = {'Authorization': token}
    q = '(= name "{}")'.format(quote(machine_name))
    url = urljoin(url, "/api/v1/machine?q={}&show_all=false".format(q))
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    if len(r.json()) == 0:
        raise ProvisionerError('Error no assigned machine found with name "{}"'.
                format(machine_name))
    if len(r.json()) > 1:
        raise ProvisionerError('Error more than one machine found with name "{}", {}'.
                format(machine_name, r.json()))
    return r.json()[0]

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
