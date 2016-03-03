#!/usr/bin/env python3
import sys
import datetime
import subprocess

def add_group(jail, group):
    """add_group
    Adds a specific user to their own group.

    Args:
        Jail - Current jail to make modification in
        Group - The name of the group that needs to be created
    Returns:
        None
    """
    command = ("sudo", "jexec", jail, "pw", "groupadd", group)

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        sys.exit(e.output)


def add_user(jail, user, group, gecos):
    """add_user
    Uses pw adduser to add a user to the system

    Args:
        Jail - Current jail to make modification in
        User - Current user to add to the jail
        Group - The group to add the current user to
        Gecos - Personal information related to the user
    Returns:
        None
    """
    command = ("sudo", "jexec", jail, "pw", "useradd",
            "-n", user,
            "-c", gecos,
            "-g", group,
            "-G", "wheel",
            "-m",
            "-k", "/usr/share/skel",
            "-s", "/bin/tcsh",
            "-w", "random")

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        sys.exit(e.output)


def set_password_expiration(jail, user):
    """set_account_expiration
    Sets the account expiration to 120 days after creation

    Args:
        Jail - Current jail to make modification in
        User - The user to set the password expiration date on
    Returns:
        None
    """
    exp_date = datetime.date.today() + datetime.timedelta(120)
    exp_date = exp_date.strftime("%m-%b-%Y")
    command = ("sudo", "jexec", jail, "pw", "usermod",
            "-p", exp_date,
            "-n", user)

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        sys.exit(e.output)


def send_msg():
    """send_msg
    Uses information from adduser cmdline progrm to send
    a user mail that can be checked during their first login

    Args:

    Returns:

    """


def drop_keys():
    """drop_keys
    Places public key into authorized_keys inside the .ssh
    folder

    Args:

    Returns:
    """


if __name__ == '__main__':
    #Do stuff
    #for testing....

    new_jail = "example"
    user_groups = ["test01", "test02", "test03", "test04"]
    user_names = ["test01", "test02", "test03", "test04"]
    user_gecos = ["test 01", "test 02", "test 03", "test 04"]

    for user, group, gecos  in zip(user_names, user_groups, user_gecos):
        print("Adding {} as a group.".format(group))
        add_group(new_jail, group)
        print("Adding {} as a user.".format(user))
        add_user(new_jail, user, group, gecos)
        print("Setting password expiration date for {}".format(user))
        set_password_expiration(new_jail, user)
