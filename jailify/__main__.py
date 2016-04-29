import os
import re
import sys
import click
import functools
import jailify.users as ju
import jailify.delete as jd
import jailify.extract as je
import jailify.creation as jc

from jailify.util import msg, create_snapshot, CommandError


PROG_NAME = os.path.basename(sys.argv and sys.argv[0] or __file__)

def root_check(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        if os.geteuid() != 0:
            sys.exit(msg(PROG_NAME, 'error', 'red', 'must be run as root'))
        else:
            func(*args, **kwargs)
    return _wrapper


@root_check
@click.command()
@click.argument('jail_directory', type=click.Path(exists=True, readable=True))
def jailify_main(jail_directory):

    try:
        file_type = je.determine_file_type(jail_directory)
    except je.InvalidFileType as err:
        sys.exit(msg(PROG_NAME, 'error', 'red', err.message))

    try:
        metadata = je.get_metadata(file_type, jail_directory)
    except (je.FailedToExtractFile, je.ExtraneousPublicKey, 
            je.InvalidJSONError, je.ValidationError, je.InvalidHostname,
            je.InvalidMetadata, je.InvalidFileType) as err:
        sys.exit(msg(PROG_NAME, 'error', 'red', err.message))

    jail_name = metadata['hostname']
    jail_name = jail_name.replace('-', '_')
    click.echo(msg(PROG_NAME, 'info', 'cyan', "creating {} jail".format(jail_name)))

    try:
        lowest_ip = jc.get_lowest_ip()
        interface = jc.get_interface()
        snapshot = jc.get_latest_snapshot()
        if jc.check_name(jail_name):
            click.echo(msg(PROG_NAME, 'info', 'cyan', 'adding entry to /etc/jail.conf'))
            jc.add_entry(lowest_ip, jail_name, interface)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "creating /etc/fstab.{}".format(jail_name)))
            jc.create_fstab_file(jail_name)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "cloning base jail at snapshot {}".format(snapshot)))
            jc.clone_base_jail(snapshot, jail_name)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "starting {} jail".format(jail_name)))
            jc.start_jail(jail_name)
        else:
            raise jc.InvalidJailNameError("jail {} already exists".format(jail_name))
    except (jc.InvalidJailNameError, jc.RegularExpressionError, CommandError) as err:
        sys.exit(msg(PROG_NAME, 'error', 'red', err.message))
   
    usernames = []
    user_gecos = []
    user_keys = []

    for user in metadata['teamMembers']:
        usernames.append(user['username'])
        user_gecos.append(user['name'])
        user_keys.append(user['publicKey'])

    try:
        user_data = zip(usernames, usernames, user_gecos, user_keys)
        for user, group, gecos, key in user_data:
            click.echo(msg(PROG_NAME, 'info', 'cyan', "adding group {}".format(group)))
            ju.add_group(jail_name, group)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "adding user {}".format(user)))
            ju.add_user(jail_name, user, group, gecos)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "setting password expiration for {}".format(user)))
            ju.set_password_expiration(jail_name, user)

            click.echo(msg(PROG_NAME, 'info', 'cyan', "placing SSH key for {}".format(user)))
            ju.add_key(jail_name, user, key)
    except (ju.SSHKeyError, ju.SendMailError, CommandError) as err:
        sys.exit(msg(PROG_NAME, 'error', 'red', err.message))

    click.echo(msg(PROG_NAME, 'info', 'cyan', "creating fallback snapshot".format(user)))
    create_snapshot(jail_name)

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
        sys.exit(msg(PROG_NAME, 'error', 'red', 'the specified jail cannot be found'))
    else:
        destroy = click.confirm(msg(PROG_NAME, 'prompt', 'magenta', "destroy {}?".format(jail_name)), default=False)
        if destroy:
            confirm_destroy = click.confirm(msg(PROG_NAME, 'WARNING', 'yellow', "this will destroy ALL jail data for {}".format(jail_name)), default=False)
            if confirm_destroy:
                click.echo(msg(PROG_NAME, 'info', 'cyan', "destroying {}".format(jail_name)))
                try:
                    destroy_jail(jail_name)
                except (jd.InvalidJailName, jd.CommandError) as err:
                    sys.exit(msg(PROG_NAME, 'error', 'red', err.message))
            if abort_output:
                sys.exit(msg(PROG_NAME, 'info', 'cyan', "aborted destruction of {}".format(jail_name)))
        else:
            if abort_output:
                sys.exit(msg(PROG_NAME, 'info', 'cyan', "aborted destruction of {}".format(jail_name)))


def confirm_individual_destruction(jail_names):
    """ checks if jails should be destroyed individually

    Args:
        jail_names (list): list of all jail names in jail.conf

    Returns:
        None

    """
    single_destroy = click.confirm(msg(PROG_NAME, 'prompt', 'magenta', 'destroy them individually?'), default=False)
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
    click.echo(msg(PROG_NAME, 'info', 'cyan', 'the following jails can be destroyed:'))
    for jail_name in jail_names:
        click.echo("    - {:^10}".format(jail_name))
    destroy = click.confirm(msg(PROG_NAME, 'prompt', 'magenta', 'destroy all of them?'), default=False)
    if destroy:
        all_destroy = click.confirm(msg(PROG_NAME, 'WARNING', 'yellow', 'this will destroy ALL data for the above jails. are you sure?'), default=False)
        if all_destroy:
            for jail_name in jail_names:
                click.echo(msg(PROG_NAME, 'info', 'cyan', "destroying {}".format(jail_name)))
                try:
                    destroy_jail(jail_name)
                except (jd.InvalidJailName, jd.CommandError) as err:
                    sys.exit(msg(PROG_NAME, 'error', 'red', err.message))
        else:
            confirm_individual_destruction(jail_names)
    else:
        confirm_individual_destruction(jail_names)


def destroy_jail(jail_name):
    """Destroys a jail.

    Helper functions are called to destroy the jail. Assumes user is sure of destruction.

    Args:
        jail_name (str): the name of the jail that is to be destroyed

    Returns:
        None

    Raises:
        jailify.delete.InvalidJailName: If ``jail_name`` is empty this exception is raised.
    """
    if not jail_name:
        raise jd.InvalidJailName("jail name cannot be empty")
    else:
        click.echo(msg(PROG_NAME, 'info', 'cyan', "stopping {} jail".format(jail_name)))
        jd.stop_jail(jail_name)

        click.echo(msg(PROG_NAME, 'info', 'cyan', "destroying {} dataset".format(jail_name)))
        jd.zfs_destroy(jail_name)

        click.echo(msg(PROG_NAME, 'info', 'cyan', "removing /etc/fstab.{}".format(jail_name)))
        jd.remove_fstab(jail_name)

        click.echo(msg(PROG_NAME, 'info', 'cyan', 'modifying /etc/jail.conf'))
        jd.edit_jailconf_file(jail_name)
