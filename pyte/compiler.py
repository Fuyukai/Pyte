"""
Compiles python bytecode using `types.FunctionType`.
"""
import dis

import sys
import warnings

from pyte import tokens
from pyte.superclasses import _PyteOp, _PyteAugmentedComparator
from pyte.exc import CompileError, ValidationError, CompileWarning
import inspect
import types


def _compile_bc(code: list) -> bytes:
    """
    Compiles Pyte objects into a bytecode string.
    """
    bc = b""
    for op in code:
        # Get the bytecode.
        if isinstance(op, _PyteOp) or isinstance(op, _PyteAugmentedComparator):
            bc_op = op.to_bytes(bc)
        elif isinstance(op, int):
            bc_op = op.to_bytes(1, byteorder="little")
        elif isinstance(op, bytes):
            bc_op = op
        else:
            raise CompileError("Could not compile code of type {}".format(type(op)))
        # Append it
        bc += bc_op

    return bc


def _simulate_stack(code: list) -> int:
    """
    Simulates the actions of the stack, to check safety.

    This returns the maximum needed stack.
    """

    max_stack = 0
    curr_stack = 0

    def _check_stack(ins):
        if curr_stack < 0:
            raise ValidationError("Stack turned negative on instruction: {}".format(ins))
        if curr_stack > max_stack:
            return curr_stack

    # Iterate over the bytecode.
    for instruction in code:
        assert isinstance(instruction, dis.Instruction)
        if instruction.arg is not None:
            effect = dis.stack_effect(instruction.opcode, instruction.arg)
        else:
            effect = dis.stack_effect(instruction.opcode)
        curr_stack += effect
        # Re-check the stack.
        _should_new_stack = _check_stack(instruction)
        if _should_new_stack:
            max_stack = _should_new_stack

    return max_stack


def compile(code: list, consts: list, names: list, varnames: list, func_name: str = "<unknown, compiled>", arg_count=0):
    """
    Compiles a set of bytecode instructions into a working function, using Python's bytecode compiler.

    Parameters:
        code: list
            This represents a list of bytecode instructions.
            These should be Pyte-validated objects, to prevent segfaults on running the code.

        consts: list
            A list of constants.
            These constants can be any objects. They will not be validated.

        names: list
            A list of global names.
            These will be used with LOAD_GLOBAL, and functions.

        varnames: list
            A list of `parameter arguments`.

        func_name: str
            The name of the function.

        arg_count: int
            The number of arguments to have. This must be less than or equal to the number of varnames.
    """
    varnames = tuple(varnames)
    consts = tuple(consts)
    names = tuple(names)

    if arg_count > len(varnames):
        raise CompileError("arg_count > len(varnames)")

    # Compile it.
    bc = _compile_bc(code)

    # Check for a final RETURN_VALUE.
    if bc[-1] != tokens.RETURN_VALUE:
        raise CompileError("No default RETURN_VALUE. Add a `pyte.tokens.RETURN_VALUE` to the end of your bytecode if "
                           "you don't need one.")

    # Set default flags
    flags = 1 | 2 | 64

    frame_data = inspect.stack()[1]

    # Validate the stack.
    if sys.version_info[0:2] > (3, 3):
        stack_size = _simulate_stack(dis._get_instructions_bytes(bc, constants=consts, names=names, varnames=varnames))
    else:
        warnings.warn("Cannot check stack for safety. Your functions may segfault.")
        stack_size = 99

    obb = types.CodeType(
        arg_count,  # Varnames - used for arguments.
        0,  # Kwargs are not supported yet
        0,  # Length of names, not sure
        stack_size,  # Use 10 by default. TODO: up this dynamically
        flags,  # 67 is default for a normal function.
        bc,  # co_code - use the bytecode we generated.
        consts,  # co_consts
        names,  # co_names, used for global calls.
        varnames,  # arguments
        frame_data[1],  # use <unknown, compiled>
        func_name,  # co_name
        frame_data[2],  # co_firstlineno, ignore this.
        b'',  # https://svn.python.org/projects/python/trunk/Objects/lnotab_notes.txt
        (),  # freevars - no idea what this does
        ()  # cellvars - used for nested functions - we don't use these.
    )
    # Update globals
    f_globals = frame_data[0].f_globals

    # Create a function type.
    f = types.FunctionType(obb, f_globals)
    f.__name__ = func_name

    # return the func
    return f
