"""
Compiles python bytecode using `types.FunctionType`.
"""

from pyte import tokens
from pyte.superclasses import _PyteOp
from pyte.exc import CompileError
import inspect
import types


def _compile_bc(code: list) -> bytes:
    """
    Compiles Pyte objects into a bytecode string.
    """
    bc = b""
    for op in code:
        # Get the bytecode.
        if isinstance(op, _PyteOp):
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


def compile(code: list, consts: list, names: list, varnames: list, func_name: str = "<unknown, compiled>", arg_count=0,
            stack_size: int = 99):
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

        stack_size: int
            The maximum size of the function stack.
            The normal Python compiler automatically allocates this, but we set it to a high number.
            Override if you're getting random segfaults due to stack allocations.
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

    # Compile the object.
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
        frame_data.filename,  # use <unknown, compiled>
        func_name,  # co_name
        frame_data.lineno,  # co_firstlineno, ignore this.
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
