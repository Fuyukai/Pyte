"""
Test suite for Pyte.
"""
import dis
import types

import pytest as pytest

import pyte
from pyte import tokens

from pyte import exc


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


def test_comparator():
    # Test a comparator function
    consts = pyte.create_consts(1, 2)
    instructions = [
        consts[0] <= consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=[], varnames=[])

    assert func()


@pytest.mark.xfail(condition=exc.ValidationError, strict=True)
def test_bad_index():
    consts = pyte.create_consts()

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])


def test_if():
    consts = pyte.create_consts(1, 2)

    instructions = [
        pyte.ops.IF(
            conditions=[
                consts[0] < consts[1]
            ],
            body=[
                [
                    pyte.ops.LOAD_CONST(consts[1])
                ]
            ]
        ),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 2


@pytest.mark.xfail(strict=True)
def test_bad_if():
    consts = pyte.create_consts(1, 2)

    instructions = [
        pyte.ops.IF(conditions=[consts[0] < consts[1]],
                    body=[])
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert not func()


def test_store():
    consts = pyte.create_consts(2)
    varnames = pyte.create_varnames("x")

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]),
        pyte.ops.STORE_FAST(varnames[0]),
        pyte.ops.LOAD_FAST(varnames[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, varnames=varnames, names=[])

    assert func() == 2