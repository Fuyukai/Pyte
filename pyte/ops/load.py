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

    def __init__(outer_self, opcode: int, list_restriction: str):

        class _FakeInnerOP(_PyteOp):
            """
            Inner class, returned by __call__
            """

            def __init__(self, validator: object, __override_opcode: int=None, __override_list_restriction: str=None):
                super().__init__()
                # Set validators.
                self.validator = validator
                if __override_opcode:
                    self._opcode = __override_opcode
                else:
                    self._opcode = opcode

                if __override_list_restriction:
                    self._list_restriction = __override_list_restriction
                else:
                    self._list_restriction = list_restriction

            def to_bytes(self, previous) -> bytes:
                byte_string = b""
                # Add the opcode
                byte_string += self._opcode.to_bytes(1, byteorder="little")
                if isinstance(self.validator, _PyteAugmentedValidator):
                    if self.validator.list_name != self._list_restriction:
                        raise ValidationError("LOAD_ call used with wrong list.")
                    # Validate it.
                    self.validator.validate()
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

            def attr(self, attr: _PyteAugmentedValidator):
                """
                Creates an inline LOAD_ATTR call, using a validator.
                """
                # Use the __override_opcode param and __override_list_restriction
                return self, self.__class__(attr, tokens.LOAD_ATTR, "names")

        outer_self._fake_class = _FakeInnerOP

    def __call__(self, arg):
        # Create a _FakeInnerOP.
        return self._fake_class(arg)


# Define the LOAD_ operators.
LOAD_FAST = _LoadOPSuper(tokens.LOAD_FAST, "varnames")
LOAD_CONST = _LoadOPSuper(tokens.LOAD_CONST, "consts")
LOAD_ATTR = _LoadOPSuper(tokens.LOAD_ATTR, "names")
LOAD_GLOBAL = _LoadOPSuper(tokens.LOAD_GLOBAL, "names")
