## VWorkspace Live Thin Client

This repository contains all the necessary tools to build a small fedora-base live client
 to access VWorkspace thin clients.

We use this in the events we organize at EPFL to allow users to access our vms.

### Configuring the ISO

You need to add network configuration if you need wifi.

`NetworkManager` is used for networking, so the simplest way of configuring wifi,
is to look into `/etc/sysconfig/network-scripts` in your system and copy the
`ifcfg-${NETWORK_NAME}` and `keys-${NETWORK_NAME}` to `skel/etc/sysconfig/networkscripts/`
and that way the ISO will connect to the network automatically once booted


### Building the ISO

First of all, you need to get a copy of the vworkspace client.
Link within EPFL: https://vdi.epfl.ch/native/Downloads/IndexLogin

Once you have it, you need to copy it to the base directory :

`cp ${VWORKSPACE_CLIENT} ${REPOSITORY_DIRECTORY}/vworkspace.bin`

You then have two choices to build the live system :

1. with `docker`:
    
    `./build-with-docker`
    
2. standalone build:

    `./build`
    
For the standalone build you need some dependencies and a Fedora system matching the release
version you want to target.

To get the exact list of dependencies, please see the `Dockerfile`.


Once the build is completed, you will find the iso in `results/`.

You can then copy the iso to a CD, a USB, or any support of your choice.

The easiest for this is to run under linux/macOS:

    `sudo dd if=results/Polyprog-ThinClient.iso of=/dev/${your_usb_key}`
    
    
### Contributing

Some rules are important when contributing :

1. Never edit anything in `upstream-live/`. These are upstream files from Fedora and 
we don't want to have to modify them.
2. Keep in mind that the readability of the configuration is very important
3. Please make an effort to keep the size of the iso the smallest possible,
this seriously impacts build time.
