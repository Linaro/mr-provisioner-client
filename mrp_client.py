#!/usr/bin/env python3

from library.PreseedControl import PreseedControl
from helper.ClientLogger import ClientLogger

from library.common import *
import argparse

from library.ImageControl import ImageControl

class Client(object):
    def __init__(self, parser, args):
        self.parser = parser
        self.args = args
        self.log = ClientLogger(__name__, parser, args.verbose)
        try:
            self.urlhandler = URLhandler(self.args.mrp_url, self.args.mrp_token)
        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def parse(self):
        if self.args.subcommand == 'image':
            self.image(self.args.action, self.args.image_type, self.args.description,
                       self.args.arch, self.args.image_path, self.args.public,
                       self.args.knowngood)
        elif self.args.subcommand == 'preseed':
            self.preseed(self.args.action, self.args.preseed_name, self.args.preseed_path,
                         self.args.description, self.args.type, self.args.public,
                         self.args.knowngood)
        else:
            self.parser.print_help()


    def image(self, command, image_type, desc, arch, path, public, knowngood):
        image_controller = ImageControl(self.urlhandler)
        try:
            if command == 'upload':
                rc = image_controller.upload_image(image_type, desc, arch, path, public,
                                                 knowngood)
                self.log.debug(rc)
            elif command == 'check':
                if image_controller.get_image(image_type, desc, arch) is not None:
                    print('True')
                else:
                    print('False')
                    exit(2)

        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def preseed(self, command, preseed_name, preseed_file, preseed_desc,
                preseed_type, public, knowngood):
        preseed_controller = PreseedControl(self.urlhandler)
        try:
            if command == 'upload':
                rc = preseed_controller.upload_preseed(preseed_name, preseed_file,preseed_type,
                                                       preseed_desc, public, knowngood)
                self.log.debug(rc)
            elif command == 'check':
                if preseed_controller.get_preseed(preseed_name, preseed_type) is not None:
                    print("True")
                else:
                    print("False")
                    exit(2)

        except Exception as err:
            self.log.fatal(err)
            exit(1)


if __name__ == '__main__':
    """This is the point of entry of our application, not much logic here"""

    parser = argparse.ArgumentParser(description='Client to the Mr Provisioner \
                                     server for provisioning baremetal \
                                     machines.', add_help=False)
    parser.add_argument('--verbose', action='count', default=0,
                        help='The verbosity of logging output')
    parser.add_argument('--mrp-url', type=str, default='',
                        required=True, help='The URL of the MrP server')
    parser.add_argument('--mrp-token', type=str,
                        required=True, help='The authentication token to use')

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_image = subparsers.add_parser('image')
    parser_image.add_argument('--action', type=str, default='', choices=['check', 'upload'],
                              required=True, help='Check that an image is on MrP, or upload it.')
    parser_image.add_argument('--image-type', type=str, default='',
                              required=True, help='Type of the image : initrd, kernel or bootloader')
    parser_image.add_argument('--description', type=str, default='',
                              required=True, help='Description to put in MrP of the image')
    parser_image.add_argument('--arch', type=str, default='',
                              required=True, help='Compatible architecture')
    parser_image.add_argument('--public', action='store_true', default=False,
                              help='Switches public flag on/off')
    parser_image.add_argument('--knowngood', action='store_true', default=False,
                              help='Switches the known good flag')
    parser_image.add_argument('--image-path', type=str, default='',
                              help='Path to the image file to upload')

    parser_preseed = subparsers.add_parser('preseed')
    parser_preseed.add_argument('--action', type=str, choices=['check', 'upload'],
                                required=True, default='')
    parser_preseed.add_argument('--preseed-name', type=str, default='',
                                required=True, help='Name of the preseed in MrP')
    parser_preseed.add_argument('--preseed-path', type=str, default='',
                                help='Path to the preseed file')
    parser_preseed.add_argument('--type', type=str, choices=['kickstart', 'preseed'],
                                default=None, help='Type of the preseed file')
    parser_preseed.add_argument('--description', type=str, default='',
                                help='Description of the preseed file in MrP')
    parser_preseed.add_argument('--knowngood', action='store_true', default=False,
                                help='Switches known good flag')
    parser_preseed.add_argument('--public', action='store_true', default=False,
                                help='Switches public flag')

    Client(parser, parser.parse_args()).parse()
