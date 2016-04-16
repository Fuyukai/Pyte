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

            def __init__(self, validators: tuple):
                super().__init__()
                # Set validators.
                self.validators = validators

            def to_bytes(self) -> bytes:
                byte_string = b""
                # Add the opcode
                byte_string += opcode.to_bytes(1, byteorder="big")
                # Go through the validators.
                for val in self.validators:
                    if isinstance(val, _PyteAugmentedValidator):
                        var = val.get()
                    elif isinstance(val, int):
                        var = val
                    else:
                        raise ValidationError("Could not turn `{}` into bytecode.".format(val))
                    # Convert var into bytestring
                    b_var = var.to_bytes(1, byteorder="big")
                    byte_string += b_var
                return byte_string

        self._fake_class = _FakeInnerOP

    def __call__(self, *args, **kwargs):
        # Create a _FakeInnerOP.
        return self._fake_class(args)

# Define the LOAD_ operators.
LOAD_FAST = _LoadOPSuper(tokens.LOAD_FAST)
LOAD_CONST = _LoadOPSuper(tokens.LOAD_CONST)
