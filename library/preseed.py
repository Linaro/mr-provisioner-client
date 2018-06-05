#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import urljoin
from common import ProvisionerError

class PreseedUploader(object):
    """ This class handles the job of uploading a preseed file to MrP.
        It shall only be called if there is a file to be uploaded, else you can
        fetch the thing via the regular call in the Ansible role"""
    def __init__(self, mrp_url, mrp_token, preseed_file, preseed_name,
                 preseed_type, preseed_desc='', preseed_knowngood=False,
                 preseed_public=False):
        self.url = mrp_url
        self.authhead = {'Authorization': mrp_token}
        self.file = preseed_file
        self.name = preseed_name
        self.type = preseed_type
        self.id = None
        self.desc = preseed_desc
        self.knowngood = preseed_knowngood
        self.public = preseed_public

    def _check_for_existence(self):
        url = urljoin(self.url, '/api/v1/preseed?show_all=true')
        r = requests.get(url, headers=self.authhead)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                                                r.status_code, r.reason))

        for preseed in r.json():
            if preseed['name'] == self.name:
                self.id = preseed['id']
                return True

        return False

    def _get_preseed_from_file(self):
        json_preseed = {}
        contents = ''

        with open(self.file, 'r') as fd:
            lines = fd.readlines()

        for line in lines:
            contents += line

        json_preseed['content'] = contents
        json_preseed['name'] = self.name
        json_preseed['type'] = self.type
        json_preseed['public'] = self.public
        json_preseed['known_good'] = self.knowngood
        if self.desc != '':
            json_preseed['description'] = self.desc

        return json_preseed

    def upload_preseed(self):
        """Uploads preseed. Should check first that preseed doesn't exist, else
        it modifies preseed (separate function ?). Post to upload, Put to
        modify (+ id). Maybe implement a jinja2 syntax check ? But that should
        be done on mrp's side"""
        res = {}
        try:
            exists = self._check_for_existence()
        except ProvisionerError as e:
            res['error'] = str(e)
            return res

        if not exists and self.file == '':
            res['error'] = 'Preseed does not exist and file not given'
            return res

        if self.id != None and self.file != '':     #Exists and file given
            try:
                res = self._modify_preseed(method='PUT')
            except ProvisionerError as e:
                res['error'] = str(e)
            return res
        elif self.file != '':        #Doesn't exist and file given
            try:
                res = self._modify_preseed(method='POST')
            except ProvisionerError as e:
                res['error'] = str(e)
            return res
        else:       #Exists and file not given, is it useful fetching contents?
            return res

    def _modify_preseed(self, method):
        preseed = self._get_preseed_from_file()
        url = urljoin(self.url, '/api/v1/preseed')
        if method == 'PUT':
            if self.id == None:
                raise ProvisionerError('preseed ID is undefined, please use upload_preseed')
            url_id = '/api/v1/preseed/' + str(self.id)
            url = urljoin(self.url, url_id)
            r = requests.put(url, headers=self.authhead, data=json.dumps(preseed))
            if r.status_code != 200:
                raise ProvisionerError('Error putting preseed {} at ID {}, \
                                   HTTP {} {}'.format(self.name, url, r.status_code, r.reason))
        elif method == 'POST':
            r = requests.post(url, headers=self.authhead, data=json.dumps(preseed))
            if r.status_code != 201:
                raise ProvisionerError('Error posting preseed {}, \
                                       HTTP {} {}'.format(self.name, r.status_code, r.reason))
        else:
            raise ProvisionerError('Bad _modify_preseed call')
        return r.json()
