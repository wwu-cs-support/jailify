#!/usr/bin/env python3

import re
import sys
import subprocess

def no_name():
    """Confirms destruction of jail when no jail name has been given.

    Args:
        None
    
    Returns:
        None
    """
    with open('/etc/jail.conf', 'r') as jail_config:
        jail_config = jail_config.read()

    jail_names = re.findall("(.*(?= {))\s*", jail_config)

    for jail in jail_names:
        print("{} is allocated for destruction".format(jail))

    if input("Destroy all of them? [y/N] ") == 'y':
        for jail in jail_names:
            destroy_jail(jail)
        sys.exit(1)
    elif input("Destroy them individually? [y/N] ") == 'y':
        for jail in jail_names:
            if input("Destroy {}? [y/N] ".format(jail)) == 'y':
                destroy_jail(jail)
    else:
        print("You chose not to destroy any jails")
        sys.exit(1)

def given_name(jail_name):
    """Confirms destruction of jail when jail name has been given.

    If the user is sure they want to destroy the jail then destroy_jail is called.

    Args:
        jail_name (str): the name of the jail that is to be destroyed

    Returns:
        None
    """
    if input("Destroy {}? [y/N] ".format(jail_name)) == "y":
        destroy_jail(jail_name)
    else:
        print("You chose not to destroy {}".format(jail_name))
        sys.exit(1)

def destroy_jail(jail_name):
    """Destroys a jail.

    If the user is sure they want to destroy the jail then helper functions are called to
    destroy the jail.

    Args:
        jail_name (str): the name of the jail that is to be destroyed

    Returns:
        None
    """
    if input("[WARNING]: This will destroy ALL jail data for {}. Are you sure? [y/N] ".format(jail_name)) == 'y':
        print("Destroying " + jail_name)
        stop_jail(jail_name)
        zfs_destroy(jail_name)
        remove_fstab(jail_name)
        edit_jailconf_file(jail_name)

def stop_jail(jail_name):
    """Stops the jail.

    Runs the command 'service jail stop jail_name' to stop the jail.

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    stop_jail_cmd = ["service", "jail", "stop", jail_name]
    if(subprocess.run(stop_jail_cmd) == 0):
        print("Error stopping the jail")

def zfs_destroy(jail_name):
    """Destroys the jail.

    Destroys jail by running 'zfs destroy' followed by the path to the jail.

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    print("zfs destroy")
    zfs_path = "zroot/jail/" + jail_name
    zfs_destroy_cmd = ["zfs", "destroy", "zroot/jail/" + jail_name]
    subprocess.run(zfs_destroy_cmd)

def remove_fstab(jail_name):
    """Removes fstab file.

    Removes fstab file by calling 'rm' followed by the path to the file

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    print("removing fstab")
    fstab_path = "/etc/fstab." + jail_name
    rm_fstab = ["rm", fstab_path]
    subprocess.run(rm_fstab)

def edit_jailconf_file(jail_name):
    """Goes into /etc/jail.conf and removes corresponding entry to a given jail name

    Note: this function is currently a placeholder

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    print("edit the /etc/jail.conf file and remove the portion relating to {}".format(jail_name))

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        no_name()
    elif(len(sys.argv) == 2):
        given_name(sys.argv[1])
    else:
        print("Incorrect number of arguments")
