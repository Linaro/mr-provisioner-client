# mr-provisioner-client
Python library to use Mr-Provisioner's API

## Current Status
Right now, there are only a few modules, copied from:
https://github.com/Linaro/ansible-role-mr-provisioner/tree/master/library

Those scripts were modified in the following way:
* Fully moved from Python 2/3 (with future) to exclusive Python3
  * There isn't a single Linux distro that doesn't have Python3 available
* Removed any reference to Ansible
  * This is independent and should not have to rely on it
* Added some TODO comments, moved to raise RuntimeError

The scripts are not tested and not even guaranteed to execute (no syntax check either).

They are just here as an example to foster the discussion on a proper client.

## Current Aim

The idea is to have a library that is usable by importing in Python and running through Ansible or Bash scripts.

It should have a structured design, where common parts (like exception handling, URL assembly, response parsing) are unique and the front-facing objects/methods only use the infrastructure.

To use via Ansible, for now, a Python wrapper will be necessary. Bash will be more complicated without the command line tool below.

## Future Aim

This repository could also have a command line tool, that uses the library, and can query Mr-Provisioner via arguments / environment variables (not exclusively) and allow admins to manage Mr-Provisioner via the command line.

This would allow seamless integration with Bash and Ansible (and Puppet and Salt etc).
