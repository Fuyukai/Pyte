"""
Pyte - The Python bytecode utility.
"""
import sys

if sys.version_info[0] == 3:
    if sys.version_info[1] == 3:
        from . import tokens_33 as tokens
    elif sys.version_info[1] == 4:
        from . import tokens_34 as tokens
    elif sys.version_info[1] == 5:
        from . import tokens_35 as tokens
    elif sys.version_info[1] == 6:
        from . import tokens_36 as tokens
    else:
        raise SystemError("This version of Python 3 is not supported")
else:
    raise SystemError("This version of Python ({}) is not supported".format(sys.version_info[0]))

from .compiler import compile
from . import superclasses
from . import ops


# Helper for creating new validated lists.
def _create_validated(*args, name) -> superclasses.PyteAugmentedArgList:
    return superclasses.PyteAugmentedArgList(args, name=name)


def create_names(*args) -> superclasses.PyteAugmentedArgList:
    """
    Creates a new list of names.

    :param args: The args to use.
    """
    return _create_validated(*args, name="names")


def create_consts(*args) -> superclasses.PyteAugmentedArgList:
    """
    Creates a new list of names.

    :param args: The args to use.
    """
    return _create_validated(*args, name="consts")


def create_varnames(*args) -> superclasses.PyteAugmentedArgList:
    """
    Creates a new list of names.

    :param args: The args to use.
    """
    return _create_validated(*args, name="varnames")
