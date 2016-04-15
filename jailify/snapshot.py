from jailify.util import do_command

def create_snapshot(jail_name):
    """Creates a snapshot.

    Calls do_command to create a clean snapshot of the newly created jail.

    Args:
        jail_name (str): desired jail_name

    Returns:
        None
    """
    path = 'zfs/{}@clean'.format(jail_name)
    cmd = ['zfs', 'snapshot', path]
    do_command(cmd)
    print("Snapshot created for {} jail".format(jail_name))
