#!/usr/bin/env python3

from library.get_ip import IPGetter
from library.image import ImageUploader
from library.machine_provision import MachineProvisioner
from library.preseed import PreseedUploader
from library.common import ProvisionerError
import argparse
import ipaddress


class Client(object):
    def __init__(self, mrp_token, mrp_url):
        self.token = mrp_token
        self.url = mrp_url

    def getip(self, machine_name, interface_name='eth1'):
        ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
        return ipgetter.get_ip()

    def getmac(self, machine_name, interface_name='eth1'):
        ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
        return ipgetter.get_mac()

    def getnetmask(self, machine_name, interface_name='eth1'):
        ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
        return ipgetter.get_netmask()

    def provision(self, machine_name, preseed_name, initrd_desc, kernel_desc,
                  kernel_opts, arch, subarch):
        try:
            provisioner = MachineProvisioner(
                self.url, self.token, machine_name)
            provisioner.set_machine_parameters(preseed_name, initrd_desc,
                                               kernel_desc, kernel_opts, arch,
                                               subarch)
            provisioner.machine_provision()
            return True
        except ProvisionerError as err:
            print(err)

    def setparams(self, machine_name, preseed_name, initrd_desc, kernel_desc,
                  kernel_opts, arch, subarch):
        try:
            provisioner = MachineProvisioner(
                self.url, self.token, machine_name)
            provisioner.set_machine_parameters(preseed_name, initrd_desc,
                                               kernel_desc, kernel_opts, arch,
                                               subarch)
        except ProvisionerError as err:
            print(err)

    def im_upload(self, image_type, desc, arch, path, public, knowngood):
        try:
            im_uploader = ImageUploader(self.url, self.token)
            print(im_uploader.upload_image(image_type, desc, arch, path, public,
                                           knowngood))
            return True
        except ProvisionerError as err:
            print(err)

    def im_check(self, image_type, desc, arch):
        try:
            im_uploader = ImageUploader(self.url, self.token)
            image = im_uploader.check_existence(image_type, desc, arch)
            if not image:
                print('Image does not exist on MrP')
                print(image)
            else:
                print('Image exists on MrP')
            return True
        except ProvisionerError as err:
            print(err)

    def pres_check(self, preseed_name):
        try:
            pres_uploader = PreseedUploader(self.url, self.token, preseed_name)
            if not pres_uploader.check_for_existence():
                print('Preseed does not exist on MrP')
            else:
                print('Preseed exists on MrP')
            return True
        except ProvisionerError as err:
            print(err)

    def pres_upload(self, preseed_name, preseed_file, preseed_desc,
                    preseed_type, public, knowngood):
        try:
            pres_uploader = PreseedUploader(self.url, self.token, preseed_name)
            pres_uploader.upload_preseed(preseed_file, preseed_desc,
                                         preseed_type, public, knowngood)
            return True
        except ProvisionerError as err:
            print(err)


if __name__ == '__main__':
    """This is the point of entry of our application, not much logic here"""
    parser = argparse.ArgumentParser(description='Client to the Mr Provisioner \
                                     server for provisioning baremetal \
                                     machines.', add_help=False)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')
    parser.add_argument('-u', '--mrp-url', type=str, default='',
                        help='The URL of the MrP server')
    parser.add_argument('-t', '--mrp-token', type=str,
                        help='The authentication token to use')
    subparsers = parser.add_subparsers(dest='subcommand')

    parser_ip = subparsers.add_parser('ip')
    parser_ip.add_argument('-a', '--action', type=str, choices=['getip', 'getmac',
                                                                'getnetmask',
                                                                'getall'], default='',
                           help='getip, getmac, getnetmask, getall')
    parser_ip.add_argument('-m', '--machine', type=str, default='',
                           help='name of the machine')

    parser_machine = subparsers.add_parser('machine')

    parser_machine.add_argument('-a', '--action', type=str, default='',
                                choices=['provision', 'setparams'],
                                help='provision, setparams')
    parser_machine.add_argument('-m', '--machine', type=str, default='',
                                help='name of the machine')

    parser_machine.add_argument('-p', '--preseed-name', type=str, default='',
                                help='name of the preseed to use')
    parser_machine.add_argument('-i', '--initrd-desc', type=str, default='',
                                help='description of the initrd to use')
    parser_machine.add_argument('-k', '--kernel-desc', type=str, default='',
                                help='description of the kernel to use')
    parser_machine.add_argument('-o', '--kernel-opts', type=str, default='',
                                help='kernel options to use')
    parser_machine.add_argument('-c', '--arch', type=str, default='',
                                help='architecture of the machine as in MrP')
    parser_machine.add_argument('-s', '--subarch', type=str, default='',
                                help='subarchitecture of the machine as in MrP')

    parser_image = subparsers.add_parser('image')
    parser_image.add_argument('-a', '--action', type=str, default='', choices=['check',
                                                                               'upload'],
                              help='Check that an image is on MrP, or upload it.')
    parser_image.add_argument('-t', '--image-type', type=str, default='',
                              help='Type of the image : initrd, kernel or bootloader')
    parser_image.add_argument('-d', '--description', type=str, default='',
                              help='Description to put in MrP of the image')
    parser_image.add_argument('-c', '--arch', type=str, default='',
                              help='Compatible architecture')
    parser_image.add_argument('-p', '--public', type=str, default='false',
                              help='Switches public flag on/off')
    parser_image.add_argument('-k', '--knowngood', type=str, default='false',
                              help='Switches the known good flag')
    parser_image.add_argument('-f', '--image-path', type=str, default='',
                              help='Path to the image file to upload')

    parser_preseed = subparsers.add_parser('preseed')
    parser_preseed.add_argument('-a', '--action', type=str, choices=['check',
                                                                     'upload'],
                                default='')
    parser_preseed.add_argument('-p', '--preseed-name', type=str, default='',
                                help='Name of the preseed in MrP')
    parser_preseed.add_argument('-f', '--preseed-path', type=str, default='',
                                help='Path to the preseed file')
    parser_preseed.add_argument('-t', '--type', type=str, choices=['kickstart',
                                                                   'preseed'], default='',
                                help='Type of the preseed file')
    parser_preseed.add_argument('-d', '--description', type=str, default='',
                                help='Description of the preseed file in MrP')
    parser_preseed.add_argument('-k', '--knowngood', type=str, default='false',
                                help='Switches known good flag')
    parser_preseed.add_argument('-p', '--public', type=str, default='false',
                                help='Switches public flag')
    args = parser.parse_args()

    client = Client(args.mrp_token, args.mrp_url)
    # Thanks to subparser and the dest flag, we can do a switchcase on the
    # first one.
    if args.subcommand == 'ip':
        # Sadly, the nesting of subparsers is non trivial...
        if args.action == 'getip':
            print(client.getip(args.machine))
        if args.action == 'getmac':
            print(client.getmac(args.machine))
        if args.action == 'getnetmask':
            print(client.getnetmask(args.machine))
        if args.action == 'getall':
            print("IP: " + client.getip(args.machine))
            print("MAC: " + client.getmac(args.machine))
            print("Network: " + str(ipaddress.ip_network(client.getip(args.machine) + '/' +
                                                         client.getnetmask(args.machine), False)))
    elif args.subcommand == 'machine':
        if args.action == 'provision':
            client.provision(args.machine, args.preseed_name, args.initrd_desc,
                             args.kernel_desc, args.kernel_opts, args.arch,
                             args.subarch)
        if args.action == 'setparams':
            client.setparams(args.machine, args.preseed_name, args.initrd_desc,
                             args.kernel_desc, args.kernel_opts, args.arch,
                             args.subarch)
    elif args.subcommand == 'image':
        if args.action == 'check':
            client.im_check(args.image_type, args.description, args.arch)
        if args.action == 'upload':
            client.im_upload(args.image_type, args.description, args.arch,
                             args.image_path, args.public, args.knowngood)
    elif args.subcommand == 'preseed':
        if args.action == 'check':
            client.pres_check(args.preseed_name)
        if args.action == 'upload':
            client.pres_upload(args.preseed_name, args.preseed_path,
                               args.description, args.type,
                               args.public, args.knowngood)
    else:
        parser.print_help()
