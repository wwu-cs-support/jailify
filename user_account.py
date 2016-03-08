#!/usr/bin/env python3
import sys
import datetime
import subprocess

def add_group(jail, group):
    """Adds a specific user to their own group.

    Args:
        Jail: Current jail to make modification in.
        Group: The name of the group that needs to be created.

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
        Jail (str): Current jail to make modification in.
        User (str): Current user to add to the jail.
        Group (str): The group to add the current user to.
        Gecos (str):Personal information related to the user.
        Groups (Array): Other groups to potentially add the user to.
        Skel_dir (str): Path to the directory that every user's directory
            will be based off of.
        Shell (str): Path to the default shell a user will be using.
        Passwd_method (str): Type of password to be generated when account
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
        Jail (str): The current jail to make the modification in.
        User (str): The user to set the password expiration date on.

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
        Command (tuple) - The command that needs to be executed.

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

    Returns:

    """
    pass


def drop_keys():
    """Places public key into authorized_keys inside the .ssh
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

    for user, group, gecos  in zip(user_names, user_groups, user_gecos):
        print("Adding {} as a group.".format(group))
        add_group(new_jail, group)
        print("Adding {} as a user.".format(user))
        add_user(new_jail, user, group, gecos)
        print("Setting password expiration date for {}".format(user))
        set_password_expiration(new_jail, user)
