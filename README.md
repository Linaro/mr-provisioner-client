# mr-provisioner-client
Python library to use Mr-Provisioner's API

## Mr-Provisioner

[Mr-Provisioner](https://github.com/mr-provisioner/mr-provisioner) is a bare metal provisioner, with the capacity to register machines, reboot them in multiple ways, upload images and preseeds and associate them to machines, etc.

This client interfaces with Mr-Provisioner via its REST API, using Token authentication, and has the ability to drive its functinality from a command line interface.

The arguments are numerous and very verbose, to make it clear and simple for automation scripts to use. It is not meant for admins to replace the UI, though it's certainly possible for admins to use them (perhaps writing bash wrappers and keeping environment variables), using the client directly.

## Current Functionality

The current supported features are:

* `net`: Network functionality such as get ip/mac/mask, form a machine.
* `state`: Machine settings, provisioning, reboot.
* `image`: Check images for existence, upload new ones.
* `preseed`: Check preseeds for existence, upload new ones.

Check the [documentation](https://github.com/Linaro/mr-provisioner-client/wiki) for more details.

This does not yet make use of **all** functionality exposed by Mr-Provisioner's API, but it already allows you to upload the right images, set the right parameters in a machine and provision it using a preseed. It also allows you to query the IP settings of a machine by name, which is helpful for automation tasks.

## Future Tasks

The main areas of work are:
* Complete the implementation of the REST API features (add machines, users, query activity, refined state)
* Implement an Ansible wrapper that makes direct use of the library (not the client)
* Write some shell wrappers to use the client as a command line tool
* Create documentation on arguments, usage, range of parameters, etc.
* Write a test suite
* Make the error messages more friendly, epecially around required arguments from actions

## Testing

Unfortunately, right now all of the testing is done manually on an existing install of Mr-Provisioner. This can be a mock installation on a local machine or a production install in a real lab. We currently do both.

We also make use of the client on our production lab, so the master branch is guarantee to work at least for our purposes. However, we're not yet making full use of its features, so YMMV.

## Reporting Bugs

Please use the issue tracker / pull requests to interact with the project.
