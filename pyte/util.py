"""
Miscellaneous utilities.
"""
from . import tokens


def _generate_load_call(opcode, index):
    bs = b""
    # add the opcode
    bs += opcode.to_bytes(1, byteorder="little")
    # Add the index
    bs += index.to_bytes(2, byteorder="little")
    # return it
    return bs


def generate_load_global(index) -> bytes:
    return _generate_load_call(tokens.LOAD_GLOBAL, index)


def generate_load_fast(index) -> bytes:
    """
    Generates a LOAD_FAST operation.
    """
    return _generate_load_call(tokens.LOAD_FAST, index)


def generate_load_const(index) -> bytes:
    return _generate_load_call(tokens.LOAD_CONST, index)
