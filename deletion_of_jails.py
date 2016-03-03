###########
#MUST RUN AS SUDO
###########

#Takes in argument of jail name
#!/usr/bin/env python3

import subprocess
import sys

#sudo service jail stop example 
def stop_jail(jail_name):
    stop_jail_cmd = ["service", "jail", "stop", jail_name]
    if(subprocess.run(stop_jail_cmd) == 0):
        print("Error stopping the jail")

#sudo zfs destroy zroot/jail/example
def destroy_jail(jail_name):
    print("zfs destroy")
    zfs_path = "zroot/jail/" + jail_name
    zfs_destroy = ["zfs", "destroy", "zroot/jail/" + jail_name]
    subprocess.run(zfs_destroy)

#sudo rm /etc/fstab.example
def remove_fstab(jail_name):
    print("removing fstab")
    fstab_path = "/etc/fstab." + jail_name
    rm_fstab = ["rm", fstab_path]
    subprocess.run(rm_fstab)

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        print("The following jails are allocated for destruction: ")
    elif(len(sys.argv) == 2):
        jail_name = sys.argv[1]
        print("Deleting jail " + jail_name)
        stop_jail(jail_name)
        destroy_jail(jail_name)
        remove_fstab(jail_name)
        #edit the jail.conf file
        print("edit the /etc/jail.conf file and remove portion relating to example")
    else:
        print("Incorrect number of arguments")
