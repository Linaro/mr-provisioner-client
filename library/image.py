#!/usr/bin/env python3

import json
import requests
from urllib.parse import urljoin

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mr-provisioner-image

short_description: Manage machine images in Mr. Provisioner

description:
    Implemented:
        - Upload new image
        - Discover existing images matching a given description.
    Not implemented:
        - modifying existing image (such as known_good/public)
        - deleting existing image

options:
    description:
        description:
            - Name of the image
        required: true
    type:
        description:
            - Image type. May be 'Kernel' or 'Initrd'.
        required: true
    arch:
        description: Image architecture. e.g. arm64, x86_64
        required: true
    path:
        description: Local file path to image file.
        required: true
    url:
        description: url to provisioner instance in the form of http://192.168.0.3:5000/
        required: true
    token:
        description: Mr. Provisioner auth token
        required: true
    known_good:
        description: Mark known good. Default false.
        required: false
    public:
        description: Mark public. Default false.
        required: false

author:
    - Dan Rue <dan.rue@linaro.org>
'''

EXAMPLES = '''
# Upload a linux kernel image
- description: debian-installer staging build 471
  type: Kernel
  arch: arm64
  path: ./builds/staging/427/linux
  url: http://192.168.0.3:5000/
  token: "{{ provisioner_auth_token }}"
'''

RETURN = '''
  id: auto-assigned image id
  description: image description
  name: auto-assigned image name
  type: Kernel or Initrd
  upload_date: Date of upload
  user: User that owns the image
  known_good: true/false
  public: true/false
  arch: arm64
'''

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
                result['json'] = image

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
    headers = {'Authorization': token}
    url = urljoin(url, "/api/v1/image")
    files = {'file': open(path, 'rb')}
    data = {'q': json.dumps({
                 'description': desc,
                 'type': img_type,
                 'arch': arch,
                 'known_good': known_good,
                 'public': public,
             })
           }
    r = requests.post(url, files=files, data=data, headers=headers)
    if r.status_code != 201:
        msg = ("Error fetching {}, HTTP {} {}\nrequest data: {}\nresult json: {}".
                format(url, r.status_code, r.reason, data, r.json()))
        module.fail_json(msg=msg, **result)
    result['json'] = r.json()
    result['changed'] = True
