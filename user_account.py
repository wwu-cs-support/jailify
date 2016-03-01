#!/usr/bin/env python3
import subprocess

def add_group(jail, group):
    """add_group
    Adds a specific user to their own group. 

    Args:
        user_group which is a string

    Returns:
        success or failure

    """
    command = ["sudo", "jexec", jail, "pw", "groupadd", group]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        print("Failed to add {} as a group".format(group))
        

def add_user(jail, user, group, gecos):
    """add_user
    Uses pw adduser to add a user to the system

    Args:

    Returns:
    
    """
    print("user={}, group={}, gecos={}".format(user, group, gecos))
    command = ["sudo", "jexec", jail, "pw", "useradd",
            "-n", user,
            "-c", gecos,
            "-g", group,
            "-G", "wheel",
            "-m",
            "-k", "/usr/share/skel",
            "-s", "/bin/tcsh",
            "-w", "random"]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        print("Failed to create {}'s user account".format(user))


def send_msg():
    """send_msg
    Uses information from adduser cmdline progrm to send 
    a user mail that can be checked during their first login

    Args:

    Returns:

    """
    pass

def drop_keys():
    """drop_keys
    Places public key into authorized_keys inside the .ssh
    folder

    Args:

    Returns:
    """
    pass

if __name__ == '__main__':
    #Do stuff
    #for testing....
    new_jail = "example"
    user_groups = ["test01", "test02", "test03", "test04"]
    user_names = ["test01", "test02", "test03", "test04"]
    user_gecos = ["test 01", "test 02", "test 03", "test 04"]
  

    for g in user_groups:
        print("Adding {} as a group.".format(g))
        add_group(new_jail, g)

    for user, group, gecos  in zip(user_names, user_groups, user_gecos):
        print("Adding {} as a user.".format(user))
        add_user(new_jail, user, group, gecos)
