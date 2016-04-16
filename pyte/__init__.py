"""
Pyte package file, import some useful stuff from other functions.
"""

from .compiler import compile
from . import tokens
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
