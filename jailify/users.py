#!/usr/bin/env python3
import sys
import os.path
import datetime
import subprocess
from jailify.util import do_command
from jailify.util import do_command_with_return

class UserError(Exception):
    """An exception that is raised when there is a problem with user creation.

    Args:
        message (str): an error message

    Attributes:
        message (str): an error message
    """
    def __init__(self, message):
        self.message = message


class SSHKeyError(UserError):
    pass


class SendMailError(UserError):
    pass


def add_group(jail, group):
    """Creates a group within the given jail.

    Args:
        jail (str): Current jail to make modification in.
        group (str): The name of the group that needs to be created.

    Returns:
        None
    """
    command = ('jexec', jail, 'pw', 'groupadd', group)
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
    message_body = do_command_with_return(command)
    message_body = "Your password is {}".format(message_body.strip('\n'))
    send_msg(jail, user, message_body)


def set_password_expiration(jail, user, duration=120):
    """Sets the account expiration to 120 days after creation.

    Args:
        jail (str): The current jail to make the modification in.
        user (str): The user to set the password expiration date on.
        duration (int): The number of days before the password expires.

    Returns:
        None
    """
    exp_date = datetime.date.today() + datetime.timedelta(duration)
    exp_date = exp_date.strftime('%m-%b-%Y')
    command = ('jexec', jail, 'pw', 'usermod', '-p', exp_date, '-n', user)
    do_command(command)


def send_msg(jail, user, body, subject="Welcome"):
    """Uses information from adduser cmdline progrm to send
       a user mail that can be checked during their first login

    Args:
        jail (str): The current jail to be sending a message in.
        user (str): Name of user to send message to.
        subject (str): Header of mail to be sent to the user.
        body (str): The message body to be sent to the user.

    Returns:
        None
    """
    command = ('jexec', jail, 'mail', '-s', subject, user)
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
    except Exception as e:
        raise SendMailError(e.output)
    process.communicate(bytes(body, 'UTF-8'))
    print("Sent mail to {}.".format(user))


def add_key(jail, user, key, jail_root="/usr/jail/", home_dir="usr/home/",
            auth_key_path=".ssh/authorized_keys"):
    """Places public key into authorized_keys inside the .ssh
       folder.

    Args:
        path_to_key (str): Path to the location where the pub key lives.
        jail (str): Current jail name we are working with.
        user (str): The use who will need the authorized_key updated.

    Returns:
        None
    """
    path_to_file = os.path.join(jail_root, jail, home_dir, user, auth_key_path)
    if os.path.isfile(path_to_file):
        with open(path_to_file, "a") as f:
            if f.write(key) <= 0:
                raise SSHKeyError("jailify: error: Could not write to authorized_keys file.")
    else:
        raise SSHKeyError("jailify: error: The file {} does not exist.".format(path_to_file))


def create_users(jail, user_groups, user_names, user_gecos, user_keys):
    """Creates user accounts and places a users ssh key into their authorized_keys file

    Args:
        jail (str): Current jail name we are working with.
        user_groups (list): Each entry corresponds to a goup a user will be added to.
        user_names (list): List of user names of accounts to be created.
        user_gecos (list): Each entry corresponds to a users gecos information.
        user_keys (list): Each entry corresponds to a users public ssh key.

    Returns:
        None
    """
    for user, group, gecos, key  in zip(user_names, user_groups, user_gecos, user_keys):
        print("Adding {} as a group.".format(group))
        add_group(jail, group)
        print("Adding {} as a user.".format(user))
        add_user(jail, user, group, gecos)
        print("Setting password expiration date for {}".format(user))
        set_password_expiration(jail, user)
        print("Placing ssh-keys for {}".format(user))
        add_key(jail, user, key)
