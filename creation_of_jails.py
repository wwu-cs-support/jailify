#!/usr/bin/env python3
#note this only works if using python3.5
import re
import subprocess
import os.path
import sys
import ipaddress

def check_name(jail_name):
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if line.startswith(jail_name):
                print("Error: {} already exists as a jail name".format(jail_name))
                return False
    return True

def get_latest_snapshot():
    cmd = ["zfs", "list", "-t", "snapshot"]
    zfs_output = subprocess.run(cmd, stdout=subprocess.PIPE)
    snapshot_list = re.findall('(?<=@)\w+', str(zfs_output))
    latest_snapshot = snapshot_list[-1]
    return latest_snapshot #"p0"

def get_lowest_ip():
    jail_conf_file = open('/etc/jail.conf', 'r')
    jail_config = jail_conf_file.read()
    jail_conf_file.close()
    
    ip_addrs = re.findall("(?<=ip4.addr = )(.*);", jail_config)
    
    next_lowest_ip = ipaddress.IPv4Address(ip_addrs[0])
    print(ip_addrs)
    for ip in ip_addrs:
        if not (str(next_lowest_ip + 1) in ip_addrs):
            return str(next_lowest_ip + 1)
        addr = ipaddress.IPv4Address(ip)
        if(addr > next_lowest_ip):
            next_lowest_ip = addr
    return str(next_lowest_ip)

def add_entry(ip_addr, jail_name, interface):
    print("Adding entry to /etc/jail.conf")
    with open('/etc/jail.conf', 'a') as jail_file:
        jail_description = "\n{} {{\n    interface = \"{}\";\n    ip4.addr = {};\n}}\n".format(jail_name, interface, ip_addr)
        jail_file.write(jail_description)

def create_fstab_file(jail_name):
    print("Creating fstab file")
    path = "/etc/fstab."
    fstab_path = path + jail_name
    fstab_file = open(fstab_path, 'w')
    fstab_file.close()

def clone_base_jail(snapshot, jail_name):
    path = "zroot/jail/"
    jail_version = ".base10.2x64"
    snapshot_path = "{}{}@{}".format(path, jail_version, snapshot) #os.path
    jail_path = os.path.join(path, jail_name)

    if(subprocess.run(["zfs", "clone", snapshot_path, jail_path]) == 0):
        print("Error cloning base jail")
    else:
        print("Success cloning base jail")

def start_jail(jail_name):
    cmd = ["service", "jail", "start", jail_name]
    if(subprocess.run(cmd) == 0):
        print("Error starting jail")

if __name__ == '__main__':
    lowest_ip = get_lowest_ip()
    print("lowest ip is :" + lowest_ip)
    jail_name = str(sys.argv[1])
    interface = "em0" #xn0 on ***REMOVED*** em0 on lion
    snapshot = get_latest_snapshot()
    if check_name(jail_name):
        add_entry(lowest_ip, jail_name, interface)
        create_fstab_file(jail_name)
        clone_base_jail(snapshot, jail_name)
        start_jail(jail_name)
