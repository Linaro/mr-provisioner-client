#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from library.common import *


class PreseedControl(object):
    """ This class handles the job of uploading a preseed file to MrP.
        It shall only be called if there is a file to be uploaded, else you can
        fetch the thing via the regular call in the Ansible role"""

    def __init__(self, requester, preseed_name):
        if requester is None:
            raise ProvisionerError("Need an initialized Requester instance")
        self.requester = requester
        self.name = preseed_name

    def _get_preseed_from_file(self, preseed_file, preseed_desc, preseed_type, public=False,
                               knowngood=False):
        json_preseed = {}
        contents = ''

        with open(preseed_file, 'r') as fd:
            lines = fd.readlines()

        if len(lines) == 0:
            raise ProvisionerError("Empty Preseed File supplied")

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

    def get_preseed(self):
        url = '/api/v1/preseed?show_all=true'

        preseeds = self.requester.get(url)

        for preseed in preseeds:
            if preseed['name'] == self.name:
                return preseed

        return None

    def upload_preseed(self, preseed_file, preseed_type, preseed_desc=None,
                       public=False, knowngood=False):
        """Uploads preseed. Should check first that preseed doesn't exist, else
        it modifies preseed (separate function ?). Post to upload, Put to
        modify (+ id). Maybe implement a jinja2 syntax check ? But that should
        be done on mrp's side"""

        preseed_id = None
        preseed_id = self.get_preseed()['id']

        if preseed_file == '':
            raise ProvisionerError('File not given')

        if preseed_id is not None:
            return self._modify_preseed(preseed_id, 'PUT', preseed_file,
                                        preseed_type, preseed_desc, public,
                                        knowngood)

        else:
            return self._modify_preseed(preseed_id, 'POST', preseed_file,
                                        preseed_type, preseed_desc, public,
                                        knowngood)

    def _modify_preseed(self, preseed_id, method, preseed_file,
                        preseed_type, preseed_desc=None, public=False,
                        knowngood=False):
        preseed = self._get_preseed_from_file(preseed_file, preseed_type, preseed_desc,
                                              public, knowngood)
        url = '/api/v1/preseed'
        if method == 'PUT':
            if preseed_id is None:
                raise ProvisionerError(
                    'preseed ID is undefined, please use upload_preseed')

            url = url + '/' + str(preseed_id)
            return self.requester.put(url, data=json.dumps(preseed))

        elif method == 'POST':
            return self.requester.post(url, data=json.dumps(preseed))
