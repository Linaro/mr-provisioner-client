#!/usr/bin/env python3

import argparse

from library.common import *

from library.MachineControl import MachineControl
from library.ImageControl import ImageControl
from library.PreseedControl import PreseedControl
from helper.ClientLogger import ClientLogger

class Client(object):
    def __init__(self, parser, args):
        self.parser = parser
        self.args = args
        self.requester = Requester(self.args.mrp_url, self.args.mrp_token)
        self.log = ClientLogger(__name__, self.parser, self.args.verbose)
        self.log.debug(self.args)

    def parse(self):
        if self.args.subcommand == 'ip':
            print(self.getNetworkInfo(self.args.action, self.args.machine,
                                      self.args.interface))
        elif self.args.subcommand == 'machine':
            self.provision(self.args.machine, self.args.action, self.args.preseed_name,
                           self.args.initrd_desc, self.args.kernel_desc, self.args.kernel_opts,
                           self.args.arch, self.args.subarch)
        elif self.args.subcommand == 'image':
            self.image_upload(self.args.action, self.args.image_type, self.args.description,
                              self.args.arch, self.args.image_path, self.args.public,
                              self.args.knowngood)
        elif self.args.subcommand == 'preseed':
            self.preseed_upload(self.args.action, self.args.preseed_name, self.args.preseed_path,
                                self.args.description, self.args.type, self.args.public,
                                self.args.knowngood)
        else:
            self.parser.print_help()

    def getNetworkInfo(self, request, machine_name, interface_name='eth1'):
        try:
            machine = MachineControl(self.requester, machine_name)
            return machine.get_network_info(request, interface_name)

        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def provision(self, machine_name, action, preseed_name, initrd_desc, kernel_desc,
                  kernel_opts, arch, subarch):
        try:
            provisioner = MachineControl(self.requester, machine_name)
            rc = provisioner.set_machine_provisioning(preseed_name,
                                                      initrd_desc, kernel_desc,
                                                      kernel_opts, arch, subarch)
            self.log.debug(rc)
        except Exception as err:
            self.log.fatal(err)
            exit(1)

        if action == 'provision':
            try:
                rc = provisioner.provision_machine()
                self.log.debug(rc)
            except Exception as err:
                self.log.fatal(err)
                exit(1)

    def image_upload(self, command, image_type, desc, arch, path, public, knowngood):
        image_uploader = ImageControl(self.requester)
        try:
            if command == 'upload':
                rc = image_uploader.upload_image(image_type, desc, arch, path, public,
                                                 knowngood)
                self.log.debug(rc)
            elif command == 'check':
                if image_uploader.check_for_existence(image_type, desc, arch):
                    print('True')
                else:
                    print('False')
                    exit(2)

        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def preseed_upload(self, command, preseed_name, preseed_file, preseed_desc,
                       preseed_type, public, knowngood):
        pres_uploader = PreseedControl(self.requester, preseed_name)
        try:
            if command == 'upload':
                rc = pres_uploader.upload_preseed(preseed_file, preseed_desc,
                                                  preseed_type, public, knowngood)
                self.log.debug(rc)
            elif command == 'check':
                if pres_uploader.check_for_existence():
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
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')
    parser.add_argument('-u', '--mrp-url', type=str, default='',
                        required=True, help='The URL of the MrP server')
    parser.add_argument('-t', '--mrp-token', type=str,
                        required=True, help='The authentication token to use')

    subparsers = parser.add_subparsers(dest='subcommand')

    parser_ip = subparsers.add_parser('ip')
    parser_ip.add_argument('-a', '--action', type=str, choices=['getip', 'getmac',
                                                                'getnetmask',
                                                                'getall',
                                                                'getnetwork'], default='',
                           required=True, help='getip, getmac, getnetmask, getall')
    parser_ip.add_argument('-m', '--machine', type=str, default='',
                           required=True, help='name of the machine')
    parser_ip.add_argument('-i', '--interface', type=str, default='eth1',
                           help='name of the interface on the machine')

    parser_machine = subparsers.add_parser('machine')
    parser_machine.add_argument('-a', '--action', type=str, default='',
                                required=True, choices=['provision', 'setparams'],
                                help='provision, setparams')
    parser_machine.add_argument('-m', '--machine', type=str, default='',
                                required=True, help='name of the machine')

    parser_machine.add_argument('-n', '--preseed-name', type=str, default='',
                                required=True, help='name of the preseed to use')
    parser_machine.add_argument('-i', '--initrd-desc', type=str, default='',
                                required=True, help='description of the initrd to use')
    parser_machine.add_argument('-k', '--kernel-desc', type=str, default='',
                                required=True, help='description of the kernel to use')
    parser_machine.add_argument('-o', '--kernel-opts', type=str, default='',
                                help='kernel options to use')
    parser_machine.add_argument('-c', '--arch', type=str, default='',
                                required=True, help='architecture of the machine as in MrP')
    parser_machine.add_argument('-s', '--subarch', type=str, default='',
                                required=True, help='subarchitecture of the machine as in MrP')

    parser_image = subparsers.add_parser('image')
    parser_image.add_argument('-a', '--action', type=str, default='', choices=['check',
                                                                               'upload'],
                              required=True, help='Check that an image is on MrP, or upload it.')
    parser_image.add_argument('-t', '--image-type', type=str, default='',
                              required=True, help='Type of the image : initrd, kernel or bootloader')
    parser_image.add_argument('-d', '--description', type=str, default='',
                              required=True, help='Description to put in MrP of the image')
    parser_image.add_argument('-c', '--arch', type=str, default='',
                              required=True, help='Compatible architecture')
    parser_image.add_argument('-p', '--public', type=str, default='false',
                              help='Switches public flag on/off')
    parser_image.add_argument('-k', '--knowngood', type=str, default='false',
                              help='Switches the known good flag')
    parser_image.add_argument('-f', '--image-path', type=str, default='',
                              help='Path to the image file to upload')

    parser_preseed = subparsers.add_parser('preseed')
    parser_preseed.add_argument('-a', '--action', type=str, choices=['check',
                                                                     'upload'],
                                required=True, default='')
    parser_preseed.add_argument('-n', '--preseed-name', type=str, default='',
                                required=True, help='Name of the preseed in MrP')
    parser_preseed.add_argument('-f', '--preseed-path', type=str, default='',
                                help='Path to the preseed file')
    parser_preseed.add_argument('-t', '--type', type=str, choices=['kickstart',
                                                                   'preseed'],
                                default='', help='Type of the preseed file')
    parser_preseed.add_argument('-d', '--description', type=str, default='',
                                help='Description of the preseed file in MrP')
    parser_preseed.add_argument('-k', '--knowngood', type=str, default='false',
                                help='Switches known good flag')
    parser_preseed.add_argument('-p', '--public', type=str, default='false',
                                help='Switches public flag')

    Client(parser, parser.parse_args()).parse()
