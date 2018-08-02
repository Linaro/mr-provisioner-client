#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin
from library.common import ProvisionerError

class ImageUploader(object):
    def __init__(self, mrp_url, mrp_token):
        self.mrp_url = mrp_url
        self.mrp_token = mrp_token
        self.headers = {'Authorization': self.mrp_token}

    def check_existence(self, img_type, desc, arch):
        allowed_types = ["Kernel", "Initrd"]
        if img_type not in allowed_types:
            raise ProvisionerError("error: type is '{}'; must be one of {}".format(
                                img_type, allowed_types))

        # Determine if image is already uploaded
        url = urljoin(self.mrp_url, "/api/v1/image?show_all=true")
        r = requests.get(url, headers=self.headers)
        if r.status_code != 200:
            raise ProvisionerError('Error fetching {}, HTTP {} {}'.format(url,
                             r.status_code, r.reason))
        for image in r.json():
            if (image['description'] == desc and
                image['type'] == img_type and
                image['arch'] == arch):
                return image

        return False

    def getImageID(self, desc, image_type, arch):
        image = self.check_existence(image_type, desc, arch)
        if image != False:
            return image['id']
        else:
            raise ProvisionerError('No preseed of description {}'.format(desc))

    def upload_image(self, img_type, desc, arch, path, public, good):
        image = self.check_existence(img_type, desc, arch)
        if image != False:
            return image
        else:
            url = urljoin(self.mrp_url, "/api/v1/image")
            files = {'file': open(path, 'rb')}
            data = {'q': json.dumps({
                         'description': desc,
                         'type': img_type,
                         'arch': arch,
                         'known_good': good.lower() == 'true',
                         'public': public.lower() == 'true',
                     })
                   }
            r = requests.post(url, files=files, data=data, headers=self.headers)
            if r.status_code != 201:
                msg = ("Error fetching {}, HTTP {} {}\nrequest data: {}\nresult json: {}".
                        format(url, r.status_code, r.reason, data, r.json()))
            return r.json()
