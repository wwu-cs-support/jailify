import os
import re
import sys
import click
import functools

import jailify.util
import jailify.users
import jailify.delete
import jailify.extract
import jailify.creation

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

    metadata = jailify.extract.extract(jailify.extract.determine_file_type(jail_directory),jail_directory)

    jailify.extract.validate(metadata)

    jail_name = metadata["hostname"]

    jailify.creation.create_jail(jail_name)



@root_check
@click.command()
@click.argument('jail_name', required=False)
def dejailify_main(jail_name):
    if jail_name:
        confirmed_jail_name = find_jails(jail_name) 
        destroy_jail_prompt(confirmed_jail_name, abort_output=False)
    else:
        jail_names = find_jails(jail_name=None, all_jails=True)
        destroy_all_jails_prompt(jail_names)


def find_jails(jail_name, all_jails=False, path_jails_conf="/etc/jail.conf"):
    """ finds the necessary jail or jails to be destroyed

    Args:
        jail_name (str): The name of the jail specified to be destroyed.
        all_jails (boolean): Whether or not to search for all available
                             jails. If True find all jails, False find
                             only the specified jail name.
        path_jails_conf (str): The path to the location of the jail.conf.
    
    Returns:
        jail_names (list): List of all jails that can be destroyed.
        found_jail (str): A verified name of the jail to be destroyed. 
    """
    found_jail = None
    with open(path_jails_conf, 'r') as jail_config:
        jail_config = jail_config.read()
        if all_jails:
            jail_names = re.findall("^((?!#)\S*(?=\s*\{.*\}$))", jail_config, re.M | re.S)
            return jail_names
        else:
            regex = "^((?!#){}(?=\s*\{{.*\}}$))".format(jail_name)
            match= re.search(regex, jail_config, re.M | re.S)
            if match:
                found_jail = match.groups()[0]
                if found_jail == jail_name:
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
            confirm_destroy = click.confirm(("[WARNING]: This will destroy ALL jail data for "
                    "{}.***REMOVED***. ARE you sure?".format(jail_name)), default=False)
            if confirm_destroy:
                print("destroying {} ...........".format(jail_name))
                #Progress bar for destruction.
                #destroy_jail(jail_name)
            if abort_output:
                sys.exit("{}: info: Destruction of {} was aborted.".format(PROG_NAME, jail_name))
        else:
            if abort_output:
                sys.exit("{}: info: Destruction of {} was aborted.".format(PROG_NAME, jail_name))


def confirm_individual_destruction(jail_names):
    """ checks if jails should be destroyed individually

    Args:
        jail_names (list): list of all jail names in jail.conf

    Returns:
        None

    """
    single_destroy = click.confirm("Destroy them individually?", default=False)
    if single_destroy:
        for jail in jail_names:
            destroy_jail_prompt(jail, abort_output=False)


def destroy_all_jails_prompt(jail_names):
    """ handles confirmation for deletion of all jails

    Args:
        jail_names (list): list of all jail names in jail.conf

    Returns:
        None

    """    
    print("The following jails are allocated for destruction:") 
    for jail in jail_names:
        print("    - {:^10}".format(jail))
    destroy = click.confirm("Destroy all of them?", default=False)
    if destroy:
        all_destroy = click.confirm(("[{}]: This will destroy ALL jail data for the above jails."
        "Are you sure?".format(click.style("WARNING", fg='red'))), default=False)
        if all_destroy:
            for jail in jail_names:
                print("Destroying {}".format(jail))
                #progress bar for jail destruction
                #destroy_jail(jail)
        else:
            confirm_individual_destruction(jail_names)
    else:
        confirm_individual_destruction(jail_names)
