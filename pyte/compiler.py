"""
Compiles python bytecode using `types.FunctionType`.
"""
from pyte.superclasses import _PyteOp
from pyte.exc import CompileError
import types

DEFAULT_STACKSIZE = 10


def compile(code: list, consts: list, names: list, varnames: list, func_name: str="<unknown, compiled>"):
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
    """
    varnames = tuple(varnames)
    consts = tuple(consts)
    names = tuple(names)

    # Compile code into a series of bytes.
    bc = b""
    for op in code:
        # Get the bytecode.
        if isinstance(op, _PyteOp):
            bc_op = op.to_bytes()
        elif isinstance(op, int):
            bc_op = op.to_bytes(1, byteorder="little")
        elif isinstance(op, bytes):
            bc_op = op
        else:
            raise CompileError("Could not compile code of type {}".format(bc_op))
        # Append it
        bc += bc_op

    # Compile the object.
    obb = types.CodeType(
        len(varnames),  # Varnames - used for arguments.
        0,  # Kwargs are not supported yet
        0,  # Length of names, not sure
        DEFAULT_STACKSIZE,  # Use 10 by default. TODO: up this dynamically
        67,  # 67 is default for a normal function.
        bc,  # co_code - use the bytecode we generated.
        consts,  # co_consts
        names,  # co_names, used for global calls.
        varnames,  # arguments
        "<compiled>",  # use <unknown, compiled>
        func_name,  # co_name
        1,  # co_firstlineno, ignore this.
        b'',  # co_lnotab - no idea what this does.
        (),  # freevars - no idea what this does
        ()  # cellvars - no idea what this does
    )

    # Create a function type.
    f = types.FunctionType(obb, {})
    f.__name__ = func_name

    # return the func
    return f