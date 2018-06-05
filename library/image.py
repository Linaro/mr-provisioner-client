#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin

# TODO: This needs to be an object, like IPGetter
# or we need to flatten all as static methods
def upload_image(mrp_token, img_type, desc, arch, path, url, public, good):
    allowed_types = ["Kernel", "Initrd"]
    if img_type not in allowed_types:
        raise RuntimeError("error: type is '{}'; must be one of {}".format(
                            img_type, allowed_types))

    # Determine if image is already uploaded
    headers = {'Authorization': mrp_token}
    url = urljoin(url, "/api/v1/image?show_all=true")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise RuntimeError('Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason))
    for image in r.json():
        if (image['description'] == desc and
            image['type'] == img_type and
            image['arch'] == arch):
            #XXX Not implemented: modify existing image
            return image

    # Image does not yet exist. Upload it.
    # curl -X POST "http://192.168.0.3:5000/api/v1/image"
    # -H "accept: application/json"
    # -H "Authorization: DEADBEEF"
    # -H "content-type: multipart/form-data"
    # -F "file=@linux;type="
    # -F "q={ "description": "Example image",
    #         "type": "Kernel",
    #         "public": false,
    #         "known_good": true } "
    headers = {'Authorization': mrp_token}
    url = urljoin(url, "/api/v1/image")
    files = {'file': open(path, 'rb')}
    data = {'q': json.dumps({
                 'description': desc,
                 'type': img_type,
                 'arch': arch,
                 'known_good': good,
                 'public': public,
             })
           }
    r = requests.post(url, files=files, data=data, headers=headers)
    if r.status_code != 201:
        msg = ("Error fetching {}, HTTP {} {}\nrequest data: {}\nresult json: {}".
                format(url, r.status_code, r.reason, data, r.json()))
    return r.json()
