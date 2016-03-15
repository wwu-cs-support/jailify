import os
import sys
import functools

import jailify.util
import jailify.users
import jailify.delete
import jailify.extract
import jailify.creation_of_jails


def root_check(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        if os.geteuid() != 0:
            sys.exit("jailify: error: must be ran as root")
        else:
            func(*args, **kwargs)
    return _wrapper


@root_check
def jailify_main():
    pass

@root_check
def dejailify_main():
    pass


if __name__ == "__main__":
    jailify_main()
    defailify_main()
