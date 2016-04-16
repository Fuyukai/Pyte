"""
Basic operations.
"""

from .call import CALL_FUNCTION
from .load import LOAD_FAST, LOAD_CONST

# Shortcut operation for LOAD_CONST[0] and RETURN_VALUE.
from pyte import util
from pyte import tokens
from pyte.exc import CompileError, ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator


class END_FUNCTION(_PyteOp):
    def to_bytes(self):
        bc = b""
        # Check the consts
        try:
            none_const = self.args[0]
        except IndexError:
            raise CompileError("Could not load constant 0") from None
        # Generate a LOAD_*
        try:
            assert isinstance(none_const, _PyteAugmentedValidator)
        except AssertionError:
            raise ValidationError("Passed in constant was not validated")

        # Validate the arg
        none_const.validate()

        if none_const.list_name == "consts":
            bc += util.generate_load_const(none_const.index)
        elif none_const.list_name == "varnames":
            bc += util.generate_load_fast(none_const.index)
        bc += tokens.RETURN_VALUE.to_bytes(1, byteorder="little")
        return bc
