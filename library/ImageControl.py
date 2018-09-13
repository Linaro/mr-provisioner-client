#!/usr/bin/env python3

import json

from library.common import *

class ImageControl(object):
    def __init__(self, requester):
        self.requester = requester

    def check_for_existence(self, img_type, desc, arch):
        allowed_types = ["Kernel", "Initrd"]
        if img_type not in allowed_types:
            raise ProvisionerError("error: type is '{}'; must be one of {}".format(
                                img_type, allowed_types))

        # Determine if image is already uploaded
        url = "/api/v1/image?show_all=true"

        try:
            images = self.requester.get(url)
        except Exception as err:
            raise err

        for image in images:
            if (image['description'] == desc and
                image['type'] == img_type and
                image['arch'] == arch):
                return image

        return False

    def get_image_id(self, desc, image_type, arch):
        image = self.check_for_existence(image_type, desc, arch)
        if image:
            return image['id']
        else:
            raise ProvisionerError('No image of description {} for architecture {}'
                                   .format(desc, arch))

    def upload_image(self, img_type, desc, arch, path, public, good):
        image = self.check_for_existence(img_type, desc, arch)
        if image:
            return image
        else:
            url = "/api/v1/image"
            files = {'file': open(path, 'rb')}
            data = {'q': json.dumps({
                         'description': desc,
                         'type': img_type,
                         'arch': arch,
                         'known_good': good.lower() == 'true',
                         'public': public.lower() == 'true',
                     })
                   }

            try:
                return self.requester.post(url, files=files, data=data)
            except Exception as err:
                raise err
