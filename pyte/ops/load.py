"""
Load ops
"""
from pyte.exc import ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator
from pyte import tokens


class _LoadOPSuper(object):
    """
    Generic super class for LOAD_ operations.
    """

    def __init__(self, opcode: int):

        class _FakeInnerOP(_PyteOp):
            """
            Inner class, returned by __call__
            """

            def __init__(self, validator: object):
                super().__init__()
                # Set validators.
                self.validator = validator

            def to_bytes(self, previous) -> bytes:
                byte_string = b""
                # Add the opcode
                byte_string += opcode.to_bytes(1, byteorder="little")
                if isinstance(self.validator, _PyteAugmentedValidator):
                    # Validate it.
                    self.validator.get()
                    # Get the index.
                    var = self.validator.index
                elif isinstance(self.validator, int):
                    var = self.validator
                else:
                    raise ValidationError("Could not turn `{}` into bytecode.".format(self.validator))
                # Convert var into bytestring
                b_var = var.to_bytes(1, byteorder="little")
                byte_string += b_var
                # Add a \x00 to the edge
                byte_string += b"\x00"
                return byte_string

        self._fake_class = _FakeInnerOP

    def __call__(self, arg):
        # Create a _FakeInnerOP.
        return self._fake_class(arg)

# Define the LOAD_ operators.
LOAD_FAST = _LoadOPSuper(tokens.LOAD_FAST)
LOAD_CONST = _LoadOPSuper(tokens.LOAD_CONST)
LOAD_ATTR = _LoadOPSuper(tokens.LOAD_ATTR)
