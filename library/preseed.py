#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import urljoin
from library.common import ProvisionerError


class PreseedUploader(object):
    """ This class handles the job of uploading a preseed file to MrP.
        It shall only be called if there is a file to be uploaded, else you can
        fetch the thing via the regular call in the Ansible role"""

    def __init__(self, mrp_url, mrp_token, preseed_name):
        self.url = mrp_url
        self.headers = {'Authorization': mrp_token}
        self.name = preseed_name
        self.id = None

    def _get_preseed_from_file(self, preseed_file, preseed_desc, preseed_type, public=False,
                               knowngood=False):
        json_preseed = {}
        contents = ''

        with open(preseed_file, 'r') as fd:
            lines = fd.readlines()

        for line in lines:
            contents += line

        json_preseed['content'] = contents
        json_preseed['name'] = self.name
        json_preseed['type'] = preseed_type
        json_preseed['public'] = public == 'True'
        json_preseed['known_good'] = knowngood == 'True'
        if preseed_desc != '':
            json_preseed['description'] = preseed_desc

        return json_preseed

    def check_for_existence(self):
        url = urljoin(self.url, '/api/v1/preseed?show_all=true')
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                                                                          r.status_code, r.reason))

        for preseed in r.json():
            if preseed['name'] == self.name:
                return preseed

        return False

    def getPreseedID(self):
        try:
            preseed = self.check_for_existence()
        except ProvisionerError as err:
            print("Could not connect to check existence of preseed")
            raise

        if preseed != False:
            return preseed['id']
        else:
            return None
    def upload_preseed(self, preseed_file, preseed_type, preseed_desc=None,
                       public=False, knowngood=False):
        """Uploads preseed. Should check first that preseed doesn't exist, else
        it modifies preseed (separate function ?). Post to upload, Put to
        modify (+ id). Maybe implement a jinja2 syntax check ? But that should
        be done on mrp's side"""
        try:
            preseed_id = None
            preseed_id = self.getPreseedID()
        except ProvisionerError as err:
            print("Could not connect to upload preseed")
            raise

        if preseed_id == None and preseed_file == '':
            raise ProvisionerError('Preseed does not exist and file not given')

        if preseed_id != None and preseed_file != '':  # Exists and file given
            try:
                res = self._modify_preseed(preseed_id, 'PUT', preseed_file,
                                           preseed_type, preseed_desc, public,
                                          knowngood)
            except ProvisionerError as e:
                print("Could not modify preseed")
                raise

        elif preseed_file != '':  # Doesn't exist and file given
            try:
                res = self._modify_preseed(preseed_id, 'POST', preseed_file,
                                           preseed_type, preseed_desc, public,
                                          knowngood)
                return res
            except ProvisionerError as e:
                print("Could not upload preseed")
                raise

        else:  # Exists and file not given, is it useful fetching contents?
            return res

    def _modify_preseed(self, preseed_id, method, preseed_file,
                        preseed_type, preseed_desc=None, public=False,
                        knowngood=False):
        preseed = self._get_preseed_from_file(preseed_file, preseed_type, preseed_desc,
                                              public, knowngood)
        url = urljoin(self.url, '/api/v1/preseed')
        if method == 'PUT':
            if self.id == None:
                raise ProvisionerError(
                    'preseed ID is undefined, please use upload_preseed')
            url_id = '/api/v1/preseed/' + str(self.id)
            url = urljoin(self.url, url_id)
            r = requests.put(url, headers=self.headers,
                             data=json.dumps(preseed))
            if r.status_code != 200:
                raise ProvisionerError('Error putting preseed {} at ID {}, \
                                   HTTP {} {}'.format(self.name, url, r.status_code, r.reason))
        elif method == 'POST':
            print(json.dumps(preseed))
            r = requests.post(url, headers=self.headers,
                              data=json.dumps(preseed))
            if r.status_code != 201:
                raise ProvisionerError('Error posting preseed {}, \
                                       HTTP {} {}'.format(self.name, r.status_code, r.reason))
        else:
            raise ProvisionerError('Bad _modify_preseed call')
        return r.json()
