import sys
import subprocess

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
