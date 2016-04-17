"""
Test suite for Pyte.
"""
import dis
import types

import pyte
from pyte import tokens


def _fake_global():
    return True


def _fake_global_with_arg(arg1):
    return arg1


def test_compiler():
    # Test the compiler with a very basic instruction.
    consts = pyte.create_consts(None)
    instructions = [tokens.LOAD_CONST, 0, 0,
                    tokens.RETURN_VALUE]

    func = pyte.compile(instructions, consts, [], [])
    assert isinstance(func, types.FunctionType)
    assert func.__code__.co_consts == (None,)

    assert func() is None


def test_compiler_validated():
    # Test the compiler with a validated operation.
    consts = pyte.create_consts(None)
    instructions = [pyte.ops.END_FUNCTION(consts[0])]

    func = pyte.compile(instructions, consts, [], [])

    assert func() is None


def test_loading_consts():
    # Test the compiler loads the consts appropriately.
    consts = pyte.create_consts(176)
    instructions = [pyte.ops.END_FUNCTION(consts[0])]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 176


def test_call_function():
    # Call _fake_global
    consts = pyte.create_consts()
    names = pyte.create_names("_fake_global")
    varnames = pyte.create_names("x")

    instructions = [pyte.ops.CALL_FUNCTION(names[0], store_return=varnames[0]),
                    pyte.ops.LOAD_FAST(varnames[0]),
                    pyte.tokens.RETURN_VALUE]

    func = pyte.compile(instructions, consts, names=names, varnames=[])

    assert func() is True


def test_call_function_with_args():
    # Call _fake_global_with_arg
    consts = pyte.create_consts(19)
    names = pyte.create_names("_fake_global_with_arg")
    varnames = pyte.create_names("x")

    instructions = [
        pyte.ops.CALL_FUNCTION(names[0], consts[0], store_return=varnames[0]),
        pyte.ops.LOAD_FAST(varnames[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=names, varnames=varnames)

    assert func() == 19