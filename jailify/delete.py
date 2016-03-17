#!/usr/bin/env python3

import re
import sys
import fileinput
import subprocess
from util import do_command

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
        if input("This is a really destructive action. Are you sure you want to destroy all jails? [y/N] ") == 'y':
            for jail in jail_names:
                destroy_jail(jail)
            sys.exit(1)
        else:
            print("You chose not to destroy all of the jails. Wise decision.")
    elif input("Destroy them individually? [y/N] ") == 'y':
        for jail in jail_names:
            if input("Destroy {}? [y/N] ".format(jail)) == 'y':
                destroy_jail(jail)
    else:
        print("You chose not to destroy any jails")
        sys.exit(1)

def given_name(jail_name):
    """Confirms destruction of jail when jail name has been given.

    First checks to see if the given name is a valid jail name. If it is then
    it checks if the user is sure they want to destroy the jail. If they are,
    then destroy_jail is called.

    Args:
        jail_name (str): the name of the jail that is to be destroyed

    Returns:
        None
    """
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if line.split(' ', 1)[0] == jail_name:
                if input("Destroy {}? [y/N] ".format(jail_name)) == "y":
                    destroy_jail(jail_name)
                    sys.exit(1)
                else:
                    print("You chose not to destroy {}".format(jail_name))
                    sys.exit(1)
    print("{}: error: invalid jail name".format(jail_name))

def destroy_jail(jail_name):
    """Destroys a jail.

    If the user is sure they want to destroy the jail then helper functions are
    called to destroy the jail.

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
    else:
        print("You chose not to destroy {}".format(jail_name))

def stop_jail(jail_name):
    """Stops the jail.

    Runs the command 'service jail stop jail_name' to stop the jail.

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    stop_jail_cmd = ["service", "jail", "stop", jail_name]
    do_command(stop_jail_cmd)

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
    do_command(zfs_destroy_cmd)

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
    rm_fstab_cmd = ["rm", fstab_path]
    do_command(rm_fstab_cmd)

def edit_jailconf_file(jail_name):
    """Goes into /etc/jail.conf and removes corresponding entry to a given jail name

    Note: TODO delete new line before jail name

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    print("editing jail.conf file")
    found_jail = False
    with fileinput.input(files=("/etc/jail.conf"), inplace=True) as jail_conf:
        for line in jail_conf:
            if line.split(' ', 1)[0] == jail_name:
                found_jail = True
                continue
            elif found_jail:
                if line.startswith("}"):
                    found_jail = False
                continue
            else:
                print(line.rstrip('\n'))

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        no_name()
    elif(len(sys.argv) == 2):
        given_name(sys.argv[1])
    else:
        print("Incorrect number of arguments")
