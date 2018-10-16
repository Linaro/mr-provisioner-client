#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path

from library.common import *

class PreseedControl(object):
    """ This class handles the job of uploading a preseed file to MrP.
        It also handles the job of checking whether a preseed is already
        on MrP, and modify it in that eventuality"""

    def __init__(self, urlhandler):
        self.urlhandler = urlhandler

    def __get_preseed_from_file(self, name, preseed_file, preseed_type, preseed_desc,  public,
                                knowngood):
        json_preseed = {}
        contents = ''

        with open(preseed_file, 'r') as fd:
            lines = fd.readlines()

        for line in lines:
            contents += line

        if preseed_desc != '':
            json_preseed['description'] = preseed_desc

        json_preseed['content'] = contents
        json_preseed['name'] = name
        json_preseed['type'] = preseed_type
        json_preseed['public'] = public
        json_preseed['known_good'] = knowngood

        return json_preseed

    def get_preseed(self, name, preseed_type):
        url = '/api/v1/preseed?show_all=true'
        preseeds = self.urlhandler.get(url)

        for preseed in preseeds:
            if preseed['name'] == name:
                if preseed_type is None or preseed['type'] == preseed_type:
                    return preseed

        return None

    def get_preseed_id(self, name):
        preseed = self.get_preseed(name, None)

        if preseed is not None and 'id' in preseed and preseed['id']:
            return preseed['id']
        else:
            return None

    def upload_preseed(self, name, preseed_file, preseed_type, preseed_desc,
                       public, knowngood):
        """Uploads preseed. Should check first that preseed doesn't exist, else
        it modifies preseed (separate function ?). Post to upload, Put to
        modify (+ id). Maybe implement a jinja2 syntax check ? But that should
        be done on mrp's side"""
        url = '/api/v1/preseed'
        if preseed_type is None:
            raise ClientError("No preseed_type specified")
        if preseed_file == '':
            raise ClientError("No preseed file given, nothing to upload")
        if not os.path.isfile(preseed_file):
            raise ClientError("Preseed file's path is invalid")

        preseed = self.__get_preseed_from_file(name, preseed_file, preseed_type, preseed_desc,
                                               public, knowngood)
        preseed_id = self.get_preseed_id(name)

        if preseed_id is None:
            return self.urlhandler.post(url, data=json.dumps(preseed))
        else:
            url = url + '/' + str(preseed_id)
            return self.urlhandler.put(url, data=json.dumps(preseed))
