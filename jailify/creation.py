#!/usr/bin/env python3
import re
import sys
import os.path
import ipaddress
import subprocess
from jailify.util import do_command
from jailify.util import do_command_with_return

class CreationError(Exception):
    """An exception that is raised when creating a jail fails.

    Args:
        message (str): an error message

    Attributes:
        message (str): an error message
    """
    def __init__(self, message):
        self.message = message

class RegularExpressionError(CreationError):
    pass

class InvalidJailNameError(CreationError):
    pass

class IPAddressError(CreationError):
    pass

def get_interface():
    """Finds the correct interface.

    Finds the lowest interface by using the command ifconfig then searching through
    the output for the non loopback interface.

    Args:
        None

    Returns:
        interface (str): correct interface

    Raises:
        RegularExpressionError: If multiple interfaces are detected this exception is raised.
    """
    cmd = ('ifconfig') 
    output = do_command_with_return(cmd)

    interfaces = [i for i in re.findall(r'(^\S*):', output, re.M) if i != 'lo0']
    if(len(interfaces) == 1):
        return interfaces[0]
    else:
        raise RegularExpressionError("multiple interfaces detected. aborting due to inability to read minds. ¯\_(ツ)_/¯")

def check_name(jail_name):
    """Checks the desired jail name for availability.

    Checks the desired jail name by going through /etc/jail.conf line by line. If the
    first word in that line is the desired jail name then that jail already exists.

    Args:
        jail_name (str): desired jailname

    Returns:
        True: jail_name is a valid name for a jail
        False: jail_name is already taken and is an invalid name for a jail
    """
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if line.startswith(jail_name):
                return False
    return True

def get_latest_snapshot():
    """Finds the latest snapshot.

    Finds the latest snapshot by using a regular expression on the output of calling
    'zfs list -t snapshot'. Assumes base jail name is .base10.2x64.

    Args:
        None

    Returns:
        latest_snapshot (str): a string of the name of the latest snapshot

    Raises:
        RegularExpressionError: If no snapshots are found, this exception is raised.
    """
    cmd = ["zfs", "list", "-t", "snapshot"]
    zfs_output = do_command_with_return(cmd)

    snapshot_list = re.findall('(?<=.base10.2x64@)\S*', str(zfs_output))
    if not snapshot_list:
        raise RegularExpressionError("no snapshots found")
    else:
        return snapshot_list[-1]

def get_lowest_ip():
    """Finds the next available ip address.

    Finds the next available ip address by searching through the /etc/jail.conf file.
    Then uses a regular expression to find all ip addresses in use and the range available.
    Starting with the lowest ip in the range available for jails, if that ip is not being
    used, it is returned. The format of the range of ip addresses in /ect/jail.conf must be
    as follows: #ip-range = 127.0.0.0/24

    Args:
        None

    Returns:
        A string that is the next available ip address

    Raises:
        IPAddressError: If no ip addresses are available or no ip-range is specified in
        /etc/jail.conf, this exception is raised.
    """
    with open('/etc/jail.conf', 'r') as jail_config:
        jail_config = jail_config.read()

    ip_range = re.search("(?<=ip-range = )(.*)", jail_config)
    if not ip_range:
        raise IPAddressError("host must specify acceptable range of IP addresses")

    ip_range = ip_range.group(0)
    ip_network = list(ipaddress.IPv4Network(ip_range).hosts())[2:]
    ip_addrs = re.findall('(?<=ip4.addr = )\"*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\"*;', jail_config)

    for ip in ip_network:
        if not (str(ip) in ip_addrs):
            return str(ip)
    raise IPAddressError('no ip addresses available in range {}'.format(ip_range))

def add_entry(ip_addr, jail_name, interface):
    """Opens /etc/jail.conf and appends the file to include an entry for the new jail.

    Args:
        ip_addr (str): the next available ip address. Found by get_lowest_ip().
        jail_name (str): the name for the jail that is being created.
        interface (str): the primary interface. Found by get_interface().

    Returns:
        None
    """
    with open('/etc/jail.conf', 'a') as jail_file:
        jail_desc = ('\n\n{} {{\n'
                     '    interface = {};\n'
                     '    ip4.addr = {};\n'
                     '    host.hostname = {}.sr***REMOVED***;\n'
                     '}}').format(jail_name, interface, ip_addr,jail_name.replace('_','-'))
        jail_file.write(jail_desc)

def create_fstab_file(jail_name):
    """Creates an empty file in the /etc/ directory called fstab.jail_name where jail_name is an argument

    Args:
        jail_name (str): the name for the jail that is being created

    Returns:
        None
    """
    path = "/etc/fstab."
    fstab_path = path + jail_name
    fstab_file = open(fstab_path, 'w')
    fstab_file.close()

def clone_base_jail(snapshot, jail_name):
    """Clones the base jail.

    Args:
        snapshot (str): the latest snapshot. Found by get_latest_snapshot.
        jail_name (str): the name for the jail that is being created.

    Returns:
        None
    """
    path = "zroot/jail/"
    jail_version = ".base10.2x64"
    snapshot_path = "{}{}@{}".format(path, jail_version, snapshot)
    jail_path = os.path.join(path, jail_name)

    cmd = ["zfs", "clone", snapshot_path, jail_path]
    do_command(cmd)

def start_jail(jail_name):
    """Starts jail by running 'service jail start jail_name' where jail_name is an argument.

    Args:
        jail_name (str): the name for the jail that is being created.

    Returns:
        None
    """
    cmd = ["service", "jail", "start", jail_name]
    do_command(cmd)
