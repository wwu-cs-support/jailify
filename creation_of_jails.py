import os.path
import subprocess
import sys

def check_name(jail_name):
    #success = True
    with open('/etc/jail.conf', 'r') as jail_config:
        for line in jail_config:
            if jail_name in line:
                #print("Error: " + jail_name + " already exists as a jail name")
                print("Error: {} already exists as a jail name".format(jail_name))
                return False
    return True

def get_lowest_ip():
    return "140.160.166.14"

def add_entry(ip_addr, jail_name, interface):
    print("Adding entry to /etc/jail.conf")
    with open('/etc/jail.conf', 'a') as jail_file:
        jail_description = "\n{} {{\n    interface = \"{}\";\n    ip4.addr = {};\n}}\n".format(jail_name, interface, ip_addr)
        jail_file.write(jail_description)
        #jail_file.write('\n' + jail_name + ' {\n    interface = "' + interface + '";\n    ip4.addr = ' + ip_addr + ';\n}\n')

def create_fstab_file(jail_name):
    print("Creating fstab file")
    path = "/etc/fstab."
    subprocess.call(["touch", path + jail_name]) #create 0 byte file and write nothing in it

def clone_base_jail(snapshot, jail_name):
    print("Cloning base jail")
    path = "zroot/jail/"
    jail_version = ".base10.2x64"
    snapshot_path = "{}{}@{}".format(path, jail_version, snapshot) #os.path
    jail_path = os.path.join(path, jail_name) #"{}{}".format(path, jail_name)

    #subprocess.call(["zfs", "clone", path + jail_version + snapshot, path + jail_name])
    subprocess.call(["zfs", "clone", snapshot_path, jail_path])

def start_jail(jail_name):
    #print("Starting jail")
    cmd = ["service", "jail", "start", jail_name]
    subprocess.call(cmd)

if __name__ == '__main__':
    lowest_ip = get_lowest_ip()
    jail_name = str(sys.argv[1])
    interface = "em0" #xn0 on ***REMOVED*** em0 on lion
    if check_name(jail_name):
        add_entry(lowest_ip, jail_name, interface)
        create_fstab_file(jail_name)
        clone_base_jail("p0", jail_name) #latest snapshot on test jail may not be "p0", so extract it from `zfs list -t snapshot`
        start_jail(jail_name)
