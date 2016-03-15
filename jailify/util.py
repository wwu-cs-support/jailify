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



