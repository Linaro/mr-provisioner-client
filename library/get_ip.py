#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from urlparse import urljoin
from urllib.parse import quote

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mr_provisioner_get_ip

short_description: This is a short module fetching the ip of the machine being
provisioned from MrP. It should be then used to create a new host (dynamically)
and then do the wait_for_connection on that new host. (sadly to do that one
needs to go all the way back to the playbook).

version_added: "1.0"

description:
    - "This module has been designed to compliment the provisioning role,
    making it able to fetch the IP from MrP, making use of the available API
    for it. It should be noted that the current behaviour is of fetching the
    reserved address for an dynamic-reserved interface. If it's static or
    dynamic, the module will fetch the last address given by KEA"

options:
    mrp_url:
        description:
            - This is the URL of the Mr Provisioner
        required: true
    mrp_token:
        description:
            - This is the authentication token for MrP's API
        required: true
    machine_name:
        description:
            - This is the machine name as shown in MrP
        required: true
    interface_name:
        description:
            - This is the name of the machine's interface you'd like the IP of.
        required: true

author:
    - Baptiste Gerondeau (baptiste.gerondeau@linaro.org)
'''

EXAMPLES = '''
- name: Get IP of provisioned machine
  mr_provisioner_get_ip:
    mrp_url: "{{ mr_provisioner_url }}"
    mrp_token: "{{ mr_provisioner_auth_token }}"
    machine_name: "{{ mr_provisioner_machine_name }}"
    interface_name: "{{ mr_provisioner_interface_name|default('eth1') }}"
  register: get_ip
- debug: var=get_ip

#Note that you get the ip fetched via get_ip['ip'] : you NEED to register get_ip
#This seems overly complicated but I've found no other way to do it...
'''

RETURN = '''
ip:
    description: An.... IP !! (v4 because MrP doesn't do v6)
    type: str
'''

# TODO: This should be common to all modules
class ProvisionerError(Exception):
    def __init__(self, message):
        super(ProvisionerError, self).__init__(message)

class IPGetter(object):
    def __init__(self, mrpurl, mrptoken, machine_id, interface_name =
                 'eth1'):
        self.mrp_url = mrpurl
        self.mrp_token = mrptoken
        self.interface = interface_name
        self.machine_id = machine_id
        self.machine_ip = ''

    def get_interfaces(self):
        headers = {'Authorization': self.mrp_token}
        url = urljoin(self.mrp_url,
                      "/api/v1/machine/{}/interface".format(self.machine_id))
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(self.mrp_url, r.status_code,
                                                         r.reason))
        if len(r.json()) == 0:
            raise ProvisionerError('Error no machine with id "{}"'.format(self.machine_id))

        return r.json()

    def get_ip(self):
        try:
            interfaces = self.get_interfaces()
        except ProvisionerError as e:
            print('Could not fetch interface for machine : "{}"'.format(e))
            return 'FAILURE'

        for i in interfaces:
            if str(i['identifier']) == self.interface:
                    return i['lease_ipv4']

# TODO: This needs a more standar name (static method)
# Or we need to make sure the IPGetter object is easy to use
def get_machine_by_name(mrp_token, mrp_url, machine_name):
    """ Look up machine by name """
    headers = {'Authorization': mrp_token}
    q = '(= name "{}")'.format(quote(machine_name))
    url = urljoin(mrp_url, "/api/v1/machine?q={}&show_all=false".format(q))
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(mrp_url,
                         r.status_code, r.reason))
    if len(r.json()) == 0:
       raise ProvisionerError('Error no assigned machine found with name "{}"'.
                    format(machine_name))
    if len(r.json()) > 1:
       raise ProvisionerError('Error more than one machine found with name "{}", {}'.
                    format(machine_name, r.json()))
    return r.json()[0]
