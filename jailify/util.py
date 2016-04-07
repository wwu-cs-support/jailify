import sys
import subprocess

class InvalidJailName(Exception):
    """An exception that is raised when the jail name is invalid.

    Args:
        message (str): an error message

    Attributes:
        message (str): an error message
    """
    def __init__(self, message):
        self.message = message

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


def do_command_with_return(command):
    """Executes command and error handles when applicable.

    Args:
        command (tuple): The command that needs to be executed.

    Returns:
        result(str): A string representation of what the return of
                     the command executed would be.
    """
    try:
        result = bytes.decode(subprocess.check_output(command))
    except subprocess.CalledProcessError as e:
        sys.exit(e.output)
    return result
