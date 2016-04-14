#!/usr/bin/env python3

import re
import sys
import fileinput
import subprocess
from jailify.util import do_command
from jailify.util import InvalidJailName

def destroy_jail(jail_name):
    """Destroys a jail.

    Helper functions are called to destroy the jail. Assumes user is sure of destruction.

    Args:
        jail_name (str): the name of the jail that is to be destroyed

    Returns:
        None
    """
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
    stop_jail_cmd = ("service", "jail", "stop", jail_name)
    do_command(stop_jail_cmd)

def zfs_destroy(jail_name):
    """Destroys the jail.

    Destroys jail by running 'zfs destroy' followed by the path to the jail.

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None

    Raises:
        InvalidJailName: If ``jail_name`` is falsy this exception is raised
            to avoid destroying the entire root dataset.
    """
    if not jail_name:
        raise InvalidJailName("Jail name cannot be empty")

    zfs_path = "zroot/jail/" + jail_name
    zfs_destroy_cmd = ("zfs", "destroy", "zroot/jail/" + jail_name)
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
    rm_fstab_cmd = ("rm", fstab_path)
    do_command(rm_fstab_cmd)

def edit_jailconf_file(jail_name):
    """Goes into /etc/jail.conf and removes corresponding entry to a given jail name

    Note: Currently has to open file twice. A better way to account for extra new line would
    be to delete the line above the jail name.

    Args:
        jail_name (str): the jail that is being deleted

    Returns:
        None
    """
    print("editing jail.conf file")

    with open("/etc/jail.conf", "r") as jail_conf_file:
        jail_conf = jail_conf_file.read()

    pattern = '\s*{}+\s*\{{.*?\}}'.format(jail_name)
    jail_conf = re.sub(pattern, '', jail_conf, flags=re.S)

    with open("/etc/jail.conf", "w") as jail_conf_file:
        jail_conf_file.write(jail_conf)

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        print("No jail specified")
        sys.exit(1)
    elif(len(sys.argv) == 2):
        destroy_jail(sys.argv[1])
    else:
        print("Incorrect number of arguments")
