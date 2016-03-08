#!/usr/bin/env python3
import sys
import os.path
import datetime
import subprocess

def add_group(jail, group):
    """Creates a group within the given jail.

    Args:
        jail (str): Current jail to make modification in.
        group (str): The name of the group that needs to be created.

    Returns:
        None
    """
    command = ('sudo', 'jexec', jail, 'pw', 'groupadd', group)
    do_command(command)


def add_user(jail, user, group, gecos, groups=["wheel"],
             skel_dir="/usr/share/skel", shell="/bin/tsch",
             passwd_method="random"):
    """Uses pw adduser to add a user to the current jail.

    Args:
        jail (str): Current jail to make modification in.
        user (str): Current user to add to the jail.
        group (str): The group to add the current user to.
        gecos (str): Personal information related to the user.
        groups (list): Other groups to potentially add the user to.
        skel_dir (str): Path to the directory that every user's directory
                        will be based off of.
        shell (str): Path to the default shell a user will be using.
        passwd_method (str): Type of password to be generated when account
                             has been successfully created.

    Returns:
        None
    """
    command = (
        'sudo',
        'jexec',
        jail,
        'pw',
        'useradd',
        '-n', user,
        '-c', '"{}"'.format(gecos),
        '-g', group,
        '-G', ",".join(groups),
        '-m',
        '-k', skel_dir,
        '-s', shell,
        '-w', passwd_method
    )
    do_command(command)


def set_password_expiration(jail, user):
    """Sets the account expiration to 120 days after creation.

    Args:
        jail (str): The current jail to make the modification in.
        user (str): The user to set the password expiration date on.

    Returns:
        None
    """
    duration = 120
    exp_date = datetime.date.today() + datetime.timedelta(duration)
    exp_date = exp_date.strftime('%m-%b-%Y')
    command = ('sudo', 'jexec', jail, 'pw', 'usermod', '-p', exp_date, '-n', user)
    do_command(command)


def do_command(command):
    """Executes command and error handles when applicable.

    Args:
        command (tuple): The command that needs to be executed.

    Returns:
        None
    """
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        sys.exit(e.output)


def send_msg():
    """Uses information from adduser cmdline progrm to send
    a user mail that can be checked during their first login

    Args:
        None

    Returns:
        None
    """
    pass


def build_path(jail_root, jail, home_dir, user, ssh_dir):
    """Builds a modifiable path to a users authorized_keys file
    locating in their home directory.

    Args:
        jail_root (str): Path to where all jails exist.
        jail (str): Current jail name we are working in.
        home_dir (str): Directory needed to traverse to.
        user (str): The user who will need the authorized key updated.
        ssh_dir (str): The path to the authorized_keys file.

    Returns:
        path (str): A successfull path to the authorized_key file
                    for a user.
    """
    print("{}{}{}{}{}".format(jail_root, jail, home_dir, user, ssh_dir))
    path = os.path.join(jail_root, jail)
    print("{}".format(path))
    return path


def drop_keys(path_to_key, jail_root, jail, home_dir, user, ssh_dir):
    """Places public key into authorized_keys inside the .ssh
    folder.

    Args:
        path_to_key (str): Path to the location where the pub key lives.
        jail_root (str): Path to where all jails exist.
        jail (str): Current jail name we are working with.
        home_dir (str): Directory needed to traverse to.
        user (str): The use who will need the authorized_key updated.
        ssh_dir (str): The path to the authorized_key file.

    Returns:
        None
    """
    path_to_auth_keys = build_path(jail_root, jail, home_dir, user, ssh_dir)
    #command = ("cat", path_to_key, ">>", path_to_auth_keys)
    #try:
    #    subprocess.check_all(command)
    #except subprocess.CalledProcessError as e:
    #    sys.exit(e.output)


if __name__ == '__main__':
    #for testing....

    jail = "example"
    user_groups = ["test01", "test02", "test03", "test04"]
    user_names = ["test01", "test02", "test03", "test04"]
    user_gecos = ["test 01", "test 02", "test 03", "test 04"]

    key_path = ""
    jail_root = "/usr/jail/"
    home_dir = "/usr/home/"
    ssh_dir = "/.ssh/authorized_keys"


    
    for user, group, gecos  in zip(user_names, user_groups, user_gecos):
    #    print("Adding {} as a group.".format(group))
    #    add_group(jail, group)
    #    print("Adding {} as a user.".format(user))
    #    add_user(jail, user, group, gecos)
    #    print("Setting password expiration date for {}".format(user))
    #    set_password_expiration(jail, user)
        drop_keys(key_path, jail_root, jail, home_dir, user, ssh_dir)
