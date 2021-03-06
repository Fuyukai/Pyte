"""
File for CALL_FUNCTION.

This does a bit of optimizing out, and makes it nicer to run than manually LOAD_ing the calls.
"""
from pyte.exc import ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator
from pyte import util, tokens
from pyte.util import PY36


class CALL_FUNCTION(_PyteOp):
    """
    CALL_FUNCTION.

    This function takes one or more indexes as arguments.
    """

    def __init__(self, function, *args, store_return=None):
        # Set the function
        self.fun = function if function else None
        # TODO: Varargs.
        self.args = list(util.flatten(args))

        # Should we store on return?
        if store_return:
            self._store_list = store_return
        else:
            self._store_list = False

    def to_bytes(self, previous) -> bytes:
        # Warning: Complex code ahead!
        # A brief explaination:
        # 1) We example self.args to check what we should load.
        # 2) We generate LOAD_CONST or LOAD_FAST opcodes depending on the _name property.
        # 3) Then we use LOAD_GLOBAL to load a function.
        # 3) Then, we generate the CALL_FUNCTION opcode, using the right params.
        arg_count = len(self.args)
        bc = b""
        # Add the load_global call to load the function
        if self.fun:
            if not isinstance(self.fun, _PyteAugmentedValidator):
                raise ValidationError("Function to call must be inside names")
            # Get the function index
            self.fun.validate()
            f_index = self.fun.index
            # Generate a LOAD_GLOBAL call
            l_g = util.generate_load_global(f_index)
            bc += l_g
        # assume it's on the stack already, otherwise
        # Iterate over.
        for arg in self.args:
            try:
                assert isinstance(arg, _PyteAugmentedValidator)
            except AssertionError:
                raise ValidationError("CALL_FUNCTION args must be validated") from None
            # Validate the arg.
            arg.validate()
            # Check the list name.
            if arg.list_name == "consts":
                # Generate a LOAD_CONST call.
                bc += util.generate_load_const(arg.index)
            elif arg.list_name == "varnames":
                # Generate a LOAD_FAST call.
                bc += util.generate_load_fast(arg.index)
            else:
                raise ValidationError("Could not determine call to use with list type {}".format(arg.list_name))

        # Generate the CALL_FUNCTION call.
        bc += tokens.CALL_FUNCTION.to_bytes(1, byteorder="little")
        # Set the low byte.
        bc += arg_count.to_bytes(1, byteorder="little")
        if not PY36:
            # Set the high byte.
            # In Python 3.6, this is handled with an EXTENDED_ARGS, I guess.
            bc += b"\x00"

        # Check if we should store the response.
        if not self._store_list:
            pass
        else:
            bc += util.generate_simple_call(tokens.STORE_FAST, self._store_list.index)
        return bc


class CALL_SIMPLE(_PyteOp):
    """
    Unlike CALL_FUNCTION, this allows a very simple call.

    It doesn't load anything, rather, it just constructs the correct CALL_FUNCTION call.
    """

    def __init__(self, arg_count: int, kwargcount: int=0):
        self._args = arg_count
        self._kwargs = kwargcount

    def to_bytes(self, previous: bytes):
        # Incredibly simple, compared to CALL_FUNCTION.
        bc = b""
        bc += tokens.CALL_FUNCTION.to_bytes(1, byteorder="little")

        # Set the low byte.
        bc += self._args.to_bytes(1, byteorder="little")
        # Set the high byte.
        if not PY36:
            # no high byte, due to extended_args
            bc += self._kwargs.to_bytes(1, byteorder="little")

        return bc
