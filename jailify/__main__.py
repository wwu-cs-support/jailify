import os
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

@click.command()
@click.argument('jail_directory', type=click.Path(exists=True, readable=True))
@root_check
def jailify_main(jail_directory):
    print("In jailify main and this argument thing is working {}".format(jail_directory))


@root_check
@click.command()
@click.argument('jail_name', required=False)
def dejailify_main(jail_name):
    if jail_name:
        destroy = click.confirm("Destroy {}.***REMOVED***?".format(jail_name), default=False)
        if destroy:
            sec_destroy = click.confirm(("[WARNING]: This will destroy ALL jail data for "
                    "{}.***REMOVED***. ARE you sure?".format(jail_name)), default=False)
            if sec_destroy:
                print("destroying {} ...........".format(jail_name))
            else:
                sys.exit("dejailify: info: Destruction of {} was aborted.".format(jail_name))
        else:
            sys.exit("dejailify: info: Destruction of {} was aborted.".format(jail_name))
    else:
        print("other things happening.......")


