import re
import os.path
import sys
import subprocess

def check_name(jail_name):
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if jail_name in line:
                print("Error: {} already exists as a jail name".format(jail_name))
                return False
    return True

def get_latest_snapshot():
    list_snapshot_cmd = ["zfs", "list", "-t", "snapshot"]
    zfs_output = subprocess.run(list_snapshot_cmd, stdout=subprocess.PIPE)
    snapshot_list = re.findall('(?<=@)\w+', str(zfs_output))
    latest_snapshot = snapshot_list[-1] #[-1] returns the last index of the list
    return latest_snapshot #"p0"

def get_lowest_ip():
    return "140.160.166.14"

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
    print("Cloning base jail")
    path = "zroot/jail/"
    jail_version = ".base10.2x64"
    snapshot_path = "{}{}@{}".format(path, jail_version, snapshot) #os.path
    jail_path = os.path.join(path, jail_name) #"{}{}".format(path, jail_name)

    #subprocess.call(["zfs", "clone", path + jail_version + snapshot, path + jail_name])
    if(subprocess.run(["zfs", "clone", snapshot_path, jail_path]) == 0):
        print("Error cloning base jail")
    else:
        print("Sucess")

def start_jail(jail_name):
    cmd = ["service", "jail", "start", jail_name]
    if(subprocess.run(cmd) == 0):
        print("Error starting jail")

if __name__ == '__main__':
    lowest_ip = get_lowest_ip()
    jail_name = str(sys.argv[1])
    interface = "em0" #xn0 on ***REMOVED*** em0 on lion
    snapshot = get_latest_snapshot()
    if check_name(jail_name):
        add_entry(lowest_ip, jail_name, interface)
        create_fstab_file(jail_name)
        clone_base_jail(snapshot, jail_name) #latest snapshot on test jail may not be "p0", so extract it from `zfs list -t snapshot`
        start_jail(jail_name)
