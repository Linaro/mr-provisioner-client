#!/usr/bin/env python3

from library.get_ip import IPGetter
from helper.ClientLogger import ClientLogger

import argparse
import ipaddress


class Client(object):
    def __init__(self, mrp_token, mrp_url):
        self.token = mrp_token
        self.url = mrp_url
        self.log = ClientLogger(__name__)

    def getip(self, machine_name, interface_name='eth1'):
        try:
            ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
            return ipgetter.get_ip()
        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def getmac(self, machine_name, interface_name='eth1'):
        try:
            ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
            return ipgetter.get_mac()
        except Exception as err:
            self.log.fatal(err)
            exit(1)

    def getnetmask(self, machine_name, interface_name='eth1'):
        try:
            ipgetter = IPGetter(self.url, self.token, machine_name, interface_name)
            return ipgetter.get_netmask()
        except Exception as err:
            self.log.fatal(err)
            exit(1)


if __name__ == '__main__':
    """This is the point of entry of our application, not much logic here"""
    parser = argparse.ArgumentParser(description='Run some benchmark.')
    parser.add_argument('action', type=str, default='',
                        help='getip, getmac, getnetmask')
    parser.add_argument('machine_name', type=str, default='',
                        help='name of the machine')
    parser.add_argument('--mrp-url', type=str, default='',
                        help='The URL of the MrP server')
    parser.add_argument('--mrp-token', type=str,
                        help='The authentication token to use')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')
    args = parser.parse_args()

    client = Client(args.mrp_token, args.mrp_url)
    if args.action == 'getip':
        print(client.getip(args.machine_name))
    elif args.action == 'getmac':
        print(client.getmac(args.machine_name))
    elif args.action == 'getnetmask':
        print(client.getnetmask(args.machine_name))
    elif args.action == 'getall':
        print("IP: " + client.getip(args.machine_name))
        print("MAC: " + client.getmac(args.machine_name))
        print("Network: " + str(ipaddress.ip_network(client.getip(args.machine_name) + '/' +
                             client.getnetmask(args.machine_name), False)))
    else:
        parser.print_help()
