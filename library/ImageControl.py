#!/usr/bin/env python3

import json

from library.common import *

class ImageControl(object):
    def __init__(self, urlhandler):
        self.urlhandler = urlhandler

    def get_image(self, img_type, desc, arch):
        url = "/api/v1/image?show_all=true"
        allowed_types = ["Kernel", "Initrd", "bootloader"]
        if img_type not in allowed_types:
            raise ProvisionerError("Error: Image type is '{}'; must be one of {}".format(
                                img_type, allowed_types))

        images = self.urlhandler.get(url)

        for image in images:
            if (image['description'] == desc and
                image['type'] == img_type and
                image['arch'] == arch):
                return image

        return None

    def get_image_id(self, desc, image_type, arch):
        image = self.get_image(image_type, desc, arch)
        if image is not None and 'id' in image and image['id']:
            return image['id']

        raise ProvisionerError('No image of description {} for architecture {}'
                                .format(desc, arch))

    def upload_image(self, img_type, desc, arch, path, public, good):
        image = self.get_image(img_type, desc, arch)
        if image is not None:
            return image

        url = "/api/v1/image"
        files = {'file': open(path, 'rb')}
        data = {'q': json.dumps({
                     'description': desc,
                     'type': img_type,
                     'arch': arch,
                     'known_good': good,
                     'public': public,
                 })
               }

        return self.urlhandler.post(url, files=files, data=data)
