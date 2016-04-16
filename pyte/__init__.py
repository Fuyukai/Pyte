"""
Pyte package file, import some useful stuff from other functions.
"""

from .compiler import compile
from . import tokens
from . import superclasses

from .ops import load

# Helper for creating new validated lists.
def create_validated(*args) -> superclasses.PyteAugmentedArgList:
    return superclasses.PyteAugmentedArgList(args)
