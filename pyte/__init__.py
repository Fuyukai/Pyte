"""
Pyte package file, import some useful stuff from other functions.
"""
import sys
__version__ = "1.0.0"

if sys.version_info[1] == 2:
    from . import tokens_32 as tokens
elif sys.version_info[1] == 3:
    from . import tokens_33 as tokens
elif sys.version_info[1] == 4:
    from . import tokens_34 as tokens
elif sys.version_info[1] == 5:
    from . import tokens_35 as tokens
elif sys.version_info[1] == 6:
    from . import tokens_36 as tokens
else:
    raise SystemError("This version of Python is not supported")

from .compiler import compile
from . import superclasses
from . import ops


# Helper for creating new validated lists.
def _create_validated(*args, name) -> superclasses.PyteAugmentedArgList:
    return superclasses.PyteAugmentedArgList(args, name=name)


def create_names(*args) -> superclasses.PyteAugmentedArgList:
    return _create_validated(*args, name="names")


def create_consts(*args) -> superclasses.PyteAugmentedArgList:
    return _create_validated(*args, name="consts")


def create_varnames(*args) -> superclasses.PyteAugmentedArgList:
    return _create_validated(*args, name="varnames")
