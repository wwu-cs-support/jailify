import sys
import subprocess

from click import style

class CommandError(Exception):
    """An exception that is raised when subprocess fails.

    Args:
        message (str): an error message

    Attributes:
        message (str): an error message
    """
    def __init__(self, message):
        self.message = message


def msg(prog_name, msg_type, color, msg):
    return "{}: {}: {}".format(prog_name, style(msg_type, color), msg)


def do_command(command):
    """Executes command and error handles when applicable.

    Args:
        command (tuple): The command that needs to be executed.

    Returns:
        None
    """
    try:
        subprocess.run(command,
                       stdout=subprocess.DEVNULL,
                       check=True)
    except subprocess.CalledProcessError as e:
        raise CommandError(e.output)

def do_command_with_return(command):
    """Executes command and error handles when applicable.

    Args:
        command (tuple): The command that needs to be executed.

    Returns:
        result(str): A string representation of what the return of
                     the command executed would be.
    """
    try:
        proc = subprocess.run(command,
                              stdout=subprocess.PIPE,
                              check=True)
        result = bytes.decode(proc.stdout)
    except subprocess.CalledProcessError as e:
        raise CommandError(e.output)
    return result

def create_snapshot(jail_name):
    """Creates a snapshot.

    Calls do_command to create a clean snapshot of the newly created jail.

    Args:
        jail_name (str): desired jail_name

    Returns:
        None
    """
    path = 'zroot/jail/{}@clean'.format(jail_name)
    cmd = ('zfs', 'snapshot', path)
    do_command(cmd)
