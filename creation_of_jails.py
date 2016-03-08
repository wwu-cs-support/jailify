#!/usr/bin/env python3
import re
import sys
import os.path
import ipaddress
import subprocess

def check_name(jail_name):
    """Checks the desired jail name for availability.

    Checks the desired jail name by going through /etc/jail.conf line by line. If the 
    first word in that line is the desired jail name then that jail already exists.

    Args:
        jail_name -- desired jailname

    Returns:
        True: jail_name is a valid name for a jail
        False: jail_name is already taken and is an invalid name for a jail
"""
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if line.startswith(jail_name):
                print("Error: {} already exists as a jail name".format(jail_name))
                return False
    return True

def get_latest_snapshot():
    """Finds the latest snapshot.

    Finds the latest snapshot by using a regular expression on the output of calling
    'zfs list -t snapshot'.

    Args:
        None

    Returns:
        latest_snapshot -- a string of the name of the latest snapshot
"""
    cmd = ["zfs", "list", "-t", "snapshot"]
    zfs_output = subprocess.run(cmd, stdout=subprocess.PIPE)
    snapshot_list = re.findall('(?<=@)\S*', str(zfs_output))
    latest_snapshot = snapshot_list[-1]
    return latest_snapshot #"p0"

def get_lowest_ip():
    """Finds the next available ip address.

    Finds the next available ip address by searching through the /etc/jail.conf file. 
    Then uses a regular expression find all ip addresses being used and stores the ip 
    addresses in a sorted list. If the current ip + 1 is not in the list, that is the 
    next lowest ip.

    Args:
        None

    Returns:
        A string that is the next available ip address
"""
    jail_conf_file = open('/etc/jail.conf', 'r')
    jail_config = jail_conf_file.read()
    jail_conf_file.close()

    ip_addrs = re.findall("(?<=ip4.addr = )(.*);", jail_config)

    ip_addrs.sort()
    for ip in ip_addrs:
        ip = ipaddress.IPv4Address(ip)
        if not (str(ip + 1) in ip_addrs):
            return str(ip + 1)
    return str(ip + 1)

def add_entry(ip_addr, jail_name, interface):
    """Opens /etc/jail.conf and appends the file to include an entry for the new jail.

    Args:
        ip_addr -- the next available ip address. Found by get_lowest_ip().
        jail_name -- the name for the jail that is being created.
        interface -- the primary interface. Currently hardcoded to 'em0'.

    Returns:
        None
"""

    print("Adding entry to /etc/jail.conf")
    with open('/etc/jail.conf', 'a') as jail_file:
        jail_description = "\n{} {{\n    interface = \"{}\";\n    ip4.addr = {};\n}}\n".format(jail_name, interface, ip_addr)
        jail_file.write(jail_description)

def create_fstab_file(jail_name):
    """Creates an empty file in the /etc/ directory called fstab.jail_name where jail_name is an argument
    Argument:
        jail_name -- the name for the jail that is being created

    Returns:
        None
"""
    print("Creating fstab file")
    path = "/etc/fstab."
    fstab_path = path + jail_name
    fstab_file = open(fstab_path, 'w')
    fstab_file.close()

def clone_base_jail(snapshot, jail_name):
    """Clones the base jail.

    Arguments:
        snapshot -- the latest snapshot. Found by get_latest_snapshot.
        jail_name -- the name for the jail that is being created.

    Returns:
        None
"""
    path = "zroot/jail/"
    jail_version = ".base10.2x64"
    snapshot_path = "{}{}@{}".format(path, jail_version, snapshot) #os.path
    jail_path = os.path.join(path, jail_name)

    if(subprocess.run(["zfs", "clone", snapshot_path, jail_path]) == 0):
        print("Error cloning base jail")
    else:
        print("Success cloning base jail")

def start_jail(jail_name):
    """Starts jail by running 'service jail start jail_name' where jail_name is an argument.

    Arguments:
        jail_name -- the name for the jail that is being created.

    Returns:
        None
"""
    cmd = ["service", "jail", "start", jail_name]
    if(subprocess.run(cmd) == 0):
        print("Error starting jail")

if __name__ == '__main__':
    """Calls functions to create a jail.

    Calls all necessary functions to define variables needed to create a jail.
    Then calls all necessary functions to create the jail.

    Args:
        None

    Returns:
        None
"""
    lowest_ip = get_lowest_ip()
    jail_name = str(sys.argv[1])
    interface = "em0" #xn0 on ***REMOVED*** em0 on lion
    snapshot = get_latest_snapshot()
    if check_name(jail_name):
        add_entry(lowest_ip, jail_name, interface)
        create_fstab_file(jail_name)
        clone_base_jail(snapshot, jail_name)
        start_jail(jail_name)
    else:
        sys.exit(1)
