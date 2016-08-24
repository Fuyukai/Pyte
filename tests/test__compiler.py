"""
Test suite for Pyte.
"""
import dis
import struct
import types

import pytest as pytest
import sys

import pyte
from pyte import tokens

from pyte import exc
from pyte.util import PY36


def _fake_global():
    return True


def _fake_global_with_arg(arg1):
    return arg1


def test_compiler():
    # Test the compiler with a very basic instruction.
    consts = pyte.create_consts(None)
    # Switch based on Python version.
    if PY36:
        # Bytecode changed in Python 3.6, to be shorter.
        instructions = [tokens.LOAD_CONST, 0,
                        tokens.RETURN_VALUE]
    else:
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
    varnames = pyte.create_varnames("x")

    instructions = [pyte.ops.CALL_FUNCTION(names[0], store_return=varnames[0]),
                    pyte.ops.LOAD_FAST(varnames[0]),
                    pyte.tokens.RETURN_VALUE]

    func = pyte.compile(instructions, consts, names=names, varnames=varnames)

    assert func() is True


def test_call_function_with_args():
    # Call _fake_global_with_arg
    consts = pyte.create_consts(19)
    names = pyte.create_names("_fake_global_with_arg")
    varnames = pyte.create_varnames("x")

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


@pytest.mark.xfail(raises=exc.ValidationError, strict=True)
def test_bad_index():
    consts = pyte.create_consts()

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    func()


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


def test_addition():
    consts = pyte.create_consts(1, 2)

    instructions = [
        consts[0] + consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 3


def test_chained_addition():
    return
    consts = pyte.create_consts(1, 2, 3)

    instructions = [
        consts[0] + consts[1] + consts[2],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 6


def test_subtraction():
    consts = pyte.create_consts(3, 2)

    instructions = [
        consts[0] - consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 1


def test_chained_subtraction():
    return
    consts = pyte.create_consts(3, 2, 1)

    instructions = [
        consts[0] - consts[1] - consts[2],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 0


def test_multiplication():
    consts = pyte.create_consts(3, 2)

    instructions = [
        consts[0] * consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 6


def test_chained_multiplication():
    return
    consts = pyte.create_consts(3, 2, 2)

    instructions = [
        consts[0] * consts[1] * consts[2],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 12


def test_div():
    consts = pyte.create_consts(6, 2)

    instructions = [
        consts[0] / consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 3.0


def test_floordiv():
    consts = pyte.create_consts(3, 2)

    instructions = [
        consts[0] // consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 1


def test_nameload():
    consts = pyte.create_consts(3)
    varnames = pyte.create_varnames("x")

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]),
        pyte.ops.STORE_FAST(varnames[0]),
        consts[0] + varnames[0],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, varnames=varnames, names=[])

    assert func() == 6


@pytest.mark.xfail(strict=True)
def test_bad_mathematics():
    consts = pyte.create_consts(1, 2, 3)

    instructions = [
        consts[0] + consts[1] - consts[2],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])


def test_load_attr():
    consts = pyte.create_consts(1)
    names = pyte.create_names("bit_length")

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]),
        pyte.ops.LOAD_ATTR(names[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=names, varnames=[])

    assert func() == (1).bit_length


@pytest.mark.xfail(raises=exc.ValidationError, strict=True, reason="LOAD_FAST a const")
def test_bad_load():
    consts = pyte.create_consts(1)

    instructions = [
        pyte.ops.LOAD_FAST(consts[0]),  # LOAD_FAST a const
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=[], varnames=[])


@pytest.mark.xfail(raises=exc.CompileError)
@pytest.mark.skipif(sys.version_info[0:2] <= (3, 3), reason="Stack validation does not work on Python <3.4")
def test_bad_stack():
    # This will attempt to load an empty stack. RIP. Normally this would seg-fault, but the validator prevents this
    # from compiling by simulating the stack.
    instructions = [
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, [], [], [])


def test_attr_syntax():
    consts = pyte.create_consts(1)
    names = pyte.create_names("bit_length")

    instructions = [
        pyte.ops.LOAD_CONST(consts[0]).attr(names[0]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=names, varnames=[])

    assert func() == (1).bit_length


def test_build_list():
    # Test building a list with BUILD_LIST
    consts = pyte.create_consts(1, 2)

    instructions = [
        pyte.ops.LIST(consts[0], consts[1]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts=consts, names=[], varnames=[])

    assert func() == [1, 2]


def test_func_with_args():
    varnames = pyte.create_varnames("a")

    instructions = [
        pyte.ops.END_FUNCTION(varnames[0])
    ]

    func = pyte.compile(instructions, [], names=[], varnames=varnames, arg_count=1)

    assert func(1) == 1


def test_for_loop():
    consts = pyte.create_consts(1, 2, 3)
    varnames = pyte.create_varnames("sl", "x")
    names = pyte.create_names("append")

    instructions = [
        # Create a list
        pyte.ops.LIST(),
        pyte.ops.STORE_FAST(varnames[0]),
        pyte.ops.FOR_LOOP(
            iterator=pyte.ops.LIST(consts[0], consts[1], consts[2]),
            body=[
                # store iterated temp
                pyte.ops.STORE_FAST(varnames[1]),
                pyte.ops.LOAD_FAST(varnames[0]).attr(names[0]),
                pyte.ops.LOAD_FAST(varnames[1]),
                pyte.tokens.CALL_FUNCTION, struct.pack("<H", 1),  # Manual call function, non-validated.
                pyte.tokens.POP_TOP,
            ]
        ),
        pyte.ops.END_FUNCTION(varnames[0])
    ]

    func = pyte.compile(instructions, consts, names=names, varnames=varnames)

    assert func() == [1, 2, 3]


def test_for_with_if():
    consts = pyte.create_consts(1, 2, 3)

    instructions = [
        pyte.ops.FOR_LOOP(
            iterator=pyte.ops.LIST(consts[0]),
            body=[
                pyte.ops.IF(
                    conditions=[consts[1] < consts[2]],
                    body=[
                        [
                            pyte.ops.LOAD_CONST(consts[1]),
                            pyte.tokens.RETURN_VALUE
                        ]
                    ]
                )
            ]
        ),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, names=[], varnames=[])

    assert func() == 2


def test_modulo():
    consts = pyte.create_consts(4, 2)

    instructions = [
        consts[0] % consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 0


def test_bin_and():
    consts = pyte.create_consts(7, 2)

    instructions = [
        consts[0] & consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 2


def test_bin_or():
    consts = pyte.create_consts(10, 4)

    instructions = [
        consts[0] | consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 14


def test_bin_xor():
    consts = pyte.create_consts(3, 1)

    instructions = [
        consts[0] ^ consts[1],
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == 2


def test_built_set():
    consts = pyte.create_consts(0, 1, 2)

    instructions = [
        pyte.ops.SET(consts[0], consts[1], consts[2]),
        pyte.tokens.RETURN_VALUE
    ]

    func = pyte.compile(instructions, consts, [], [])

    assert func() == {0, 1, 2}
