"""
Miscellaneous utilities.
"""
import collections

from . import tokens


def generate_simple_call(opcode, index):
    bs = b""
    # add the opcode
    bs += opcode.to_bytes(1, byteorder="little")
    # Add the index
    bs += index.to_bytes(2, byteorder="little")
    # return it
    return bs


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