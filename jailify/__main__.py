import os
import re
import sys
import click
import functools

import jailify.util
import jailify.users
import jailify.delete
import jailify.extract
import jailify.creation_of_jails

PROG_NAME = os.path.basename(sys.argv and sys.argv[0] or __file__)

def root_check(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        if os.geteuid() != 0:
            sys.exit("{}: error: must be ran as root".format(PROG_NAME))
        else:
            func(*args, **kwargs)
    return _wrapper


@root_check
@click.command()
@click.argument('jail_directory', type=click.Path(exists=True, readable=True))
def jailify_main(jail_directory):
    print("Creating jail: {}.***REMOVED***".format(jail_directory.split(".")[0]))


@root_check
@click.command()
@click.argument('jail_name', required=False)
def dejailify_main(jail_name):
    if jail_name:
        confirmed_jail_name = find_jails(jail_name) 
        destroy_jail_prompt(confirmed_jail_name)
    else:
        jail_names = find_jails(jail_name=None, all_jails=True)
        print("The following jails are allocated for destruction:") 
        for jail in jail_names:
            print("    - {:^10}".format(jail))
        destroy = click.confirm("Destroy all of them?", default=False)
        if destroy:
            for jail in jail_names:
                print("Destroying {}".format(jail))
                #destroy_jail(jail)
        else:
            for jail in jail_names:
                destroy_jail_prompt(jail, abort_output=False)


def find_jails(jail_name, all_jails=False):
    """ finds the necessary jail or jails to be destroyed

    Args:
        jail_name (str): The name of the jail specified to be destroyed.
        all_jails (boolean): Whether or not to search for all available
                             jails. If True find all jails, False find
                             only the specified jail name.
    
    Returns:
        jail_names (list): List of all jails that can be destroyed.
        jail_name (str): A verified name of the jail to be destroyed. 
    """
    found_jail = None
    with open('/etc/jail.conf', 'r') as jail_config:
        if all_jails:
            jail_config = jail_config.read()
            jail_names = re.findall("(.*(?= {))\s*", jail_config) 
            return jail_names
        else:
            for line in jail_config:
                if line.split(' ', 1)[0] == jail_name:
                    found_jail = line.split(' ',1)[0]
            return found_jail


def destroy_jail_prompt(jail_name, abort_output=True):
    """ handles confirmation for jail destruction

    Args:
        jail_name (str): Name of jail to be destroyed.
        abort_output (boolean): Whether or not abort the program after
                                a No response. 

    Returns:
        None
    """
    if jail_name is None:
        sys.exit("{}: error: The jail specified cannot be found".format(PROG_NAME))
    else:
        destroy = click.confirm("Destroy {}.***REMOVED***?".format(jail_name), default=False)
        if destroy:
            sec_destroy = click.confirm(("[WARNING]: This will destroy ALL jail data for "
                    "{}.***REMOVED***. ARE you sure?".format(jail_name)), default=False)
            if sec_destroy:
                print("destroying {} ...........".format(jail_name))
                #destroy_jail(jail_name)
            else:
                if abort_output:
                    sys.exit("{}: info: Destruction of {} was aborted.".format(PROG_NAME, jail_name))
        else:
            if abort_output:
                sys.exit("{}: info: Destruction of {} was aborted.".format(PROG_NAME, jail_name))
