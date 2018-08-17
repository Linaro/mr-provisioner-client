#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from library.common import *


class PreseedControl(object):
    """ This class handles the job of uploading a preseed file to MrP.
        It shall only be called if there is a file to be uploaded, else you can
        fetch the thing via the regular call in the Ansible role"""

    def __init__(self, requester, preseed_name):
        self.requester = requester
        self.log = logging.getLogger(__name__)
        self.name = preseed_name

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
        url = '/api/v1/preseed?show_all=true'

        try:
            preseeds = self.requester.get(url)
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

        for preseed in preseeds:
            if preseed['name'] == self.name:
                return preseed

        return False

    def get_preseed_id(self):
        try:
            preseed = self.check_for_existence()
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

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

        preseed_id = None
        preseed_id = self.get_preseed_id()

        self.log.debug("Preseed ID: %s" % preseed_id)
        self.log.debug("Preseed_file: %s" % preseed_file)

        if preseed_id is None and preseed_file == '':
            raise ProvisionerError('Preseed does not exist and file not given')

        if preseed_id is not None and preseed_file != '':  # Exists and file given
            try:
                res = self._modify_preseed(preseed_id, 'PUT', preseed_file,
                                           preseed_type, preseed_desc, public,
                                          knowngood)
            except ProvisionerError as e:
                self.log.critical("Could not modify preseed")
                raise

        elif preseed_file != '':  # Doesn't exist and file given
            try:
                res = self._modify_preseed(preseed_id, 'POST', preseed_file,
                                           preseed_type, preseed_desc, public,
                                          knowngood)
                return res
            except ProvisionerError as e:
                self.log.critical("Could not upload preseed")
                raise

        else:  # Exists and file not given, is it useful fetching contents?
            return res

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

            try:
                response = self.requester.put(url, data=json.dumps(preseed))
            except Exception as err:
                self.log.fatal(err, exc_info=True)
                exit(1)

        elif method == 'POST':
            self.log.debug(json.dumps(preseed))

            try:
                response = self.requester.post(url, data=json.dumps(preseed))
            except Exception as err:
                self.log.fatal(err, exc_info=True)
                exit(1)

        return response
