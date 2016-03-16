import os
import sys
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
def jailify_main():
    print("In jailify main")

@root_check
def dejailify_main():
    print("In dejailify main")
