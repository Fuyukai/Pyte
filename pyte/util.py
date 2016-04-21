"""
Miscellaneous utilities.
"""
import collections
import dis

import sys

from . import tokens
import pyte


def generate_simple_call(opcode, index):
    bs = b""
    # add the opcode
    bs += opcode.to_bytes(1, byteorder="little")
    # Add the index
    if isinstance(index, int):
        bs += index.to_bytes(2, byteorder="little")
    else:
        bs += index
    # return it
    return bs


def generate_bytecode_from_obb(obb: object, previous: bytes) -> bytes:
    # Generates bytecode from a specified object, be it a validator or an int or bytes even.
    if isinstance(obb, pyte.superclasses._PyteOp):
        return obb.to_bytes(previous)
    elif isinstance(obb, (pyte.superclasses._PyteAugmentedComparator,
                          pyte.superclasses._PyteAugmentedValidator._FakeMathematicalOP)):
        return obb.to_bytes(previous)
    elif isinstance(obb, pyte.superclasses._PyteAugmentedValidator):
        obb.validate()
        return obb.to_load()
    elif isinstance(obb, int):
        return obb.to_bytes((obb.bit_length() + 7) // 8, byteorder="little") or b''
    elif isinstance(obb, bytes):
        return obb
    else:
        raise TypeError("`{}` was not a valid bytecode-encodable item".format(obb))


def generate_load_global(index) -> bytes:
    return generate_simple_call(tokens.LOAD_GLOBAL, index)


def generate_load_fast(index) -> bytes:
    """
    Generates a LOAD_FAST operation.
    """
    return generate_simple_call(tokens.LOAD_FAST, index)


def generate_load_const(index) -> bytes:
    return generate_simple_call(tokens.LOAD_CONST, index)


# https://stackoverflow.com/a/2158532
def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            for sub in flatten(el):
                yield sub
        else:
            yield el


# "fixed" functions


def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name as both value and repr if the name
       list is defined.
       Otherwise returns the name index and its repr().
    """
    argval = name_index
    if name_list is not None:
        try:
            argval = name_list[name_index]
        except IndexError:
            return "(unknown)", "(unknown)"
        argrepr = argval
    else:
        argrepr = repr(argval)
    return argval, argrepr


dis._get_name_info = _get_name_info

if sys.version_info[0:2] < (3, 4):
    from pyte import backports

    backports.apply()
