"""
STORE_FAST operation.
"""
from pyte import util, tokens
from pyte.exc import CompileError, ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator


class STORE_FAST(_PyteOp):
    """
    This represents a STORE_FAST operation.
    """

    def to_bytes(self, previous):
        # Check the first arg.
        try:
            arg = self.args[0]
        except IndexError:
            raise CompileError("No varname was passed to store in.") from None

        try:
            assert isinstance(arg, _PyteAugmentedValidator)
        except AssertionError:
            raise ValidationError("Passed in varname was not validated")

        # Validate the arg.
        arg.validate()
        # Generate a STORE_FAST opcode
        opp = util.generate_simple_call(tokens.STORE_FAST, arg.index)
        return opp