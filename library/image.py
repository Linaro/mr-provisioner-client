#!/usr/bin/env python3

import json
import logging

from library.common import *

class ImageControl(object):
    def __init__(self, requester):
        self.requester = requester
        self.log = logging.getLogger(__name__)

    def check_existence(self, img_type, desc, arch):
        allowed_types = ["Kernel", "Initrd"]
        if img_type not in allowed_types:
            raise ProvisionerError("error: type is '{}'; must be one of {}".format(
                                img_type, allowed_types))

        # Determine if image is already uploaded
        url = "/api/v1/image?show_all=true"

        try:
            images = self.requester.get(url)
        except Exception as err:
            self.log.fatal(err, exc_info=True)
            exit(1)

        for image in images:
            if (image['description'] == desc and
                image['type'] == img_type and
                image['arch'] == arch):
                return image

        return False

    def get_image_id(self, desc, image_type, arch):
        image = self.check_existence(image_type, desc, arch)
        if image:
            return image['id']
        else:
            raise ProvisionerError('No preseed of description {}'.format(desc))

    def upload_image(self, img_type, desc, arch, path, public, good):
        image = self.check_existence(img_type, desc, arch)
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
                response = self.requester.post(url, files=files, data=data)
            except Exception as err:
                self.log.fatal(err, exc_info=True)
                exit(1)

            return response
