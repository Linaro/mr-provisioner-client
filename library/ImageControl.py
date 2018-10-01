#!/usr/bin/env python3

import json

from library.common import *

class ImageControl(object):
    def __init__(self, requester):
        if requester is None:
            raise ProvisionerError("Need an initialized instance of Requester")
        self.requester = requester

    def get_image(self, desc, img_type, arch):
        allowed_types = ["Kernel", "Initrd"]
        if img_type not in allowed_types:
            raise ProvisionerError("error: type is '{}'; must be one of {}".format(
                                img_type, allowed_types))

        # Determine if image is already uploaded
        url = "/api/v1/image?show_all=true"

        images = self.requester.get(url)

        for image in images:
            if (image['description'] == desc and
                image['type'] == img_type and
                image['arch'] == arch):
                return image

        raise ProvisionerError('No image of description {} for architecture {}'
                                   .format(desc, arch))

    def upload_image(self, img_type, desc, arch, path, public, good):
        image = self.get_image(desc, img_type, arch)
        if image:
            return image
        else:
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

            return self.requester.post(url, files=files, data=data)
