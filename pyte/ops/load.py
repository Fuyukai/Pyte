"""
Load ops
"""
from pyte.exc import ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator
from pyte import tokens, util


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
                return _AttrLoader(self, attr)

        outer_self._fake_class = _FakeInnerOP

    def __call__(self, arg):
        # Create a _FakeInnerOP.
        return self._fake_class(arg)


class _AttrLoader(_PyteOp):
    """
    Custom class for a LOAD_ATTR call.

    Allows chained .attr calls.
    """

    def __init__(self, item: _PyteAugmentedValidator, first_attr):
        # This should be the original item to LOAD_FAST/_NAME/_GLOBAL or whatever.
        self.item = item

        # Attrs.
        self._attrs = [first_attr]

    def to_bytes(self, previous: bytes):
        bc = b""
        # Add the LOAD_ call.
        bc += util.generate_bytecode_from_obb(self.item, b"")
        # Add the attribute calls.
        for attr in self._attrs:
            try:
                assert isinstance(attr, _PyteAugmentedValidator)
            except AssertionError:
                raise ValidationError("LOAD_ATTR call was not a _PyteAugmentedValidator object") from None

            # Generate a LOAD_ATTR call
            attr.validate()
            bc += util.generate_simple_call(tokens.LOAD_ATTR, attr.index)

        return bc

    def attr(self, item: _PyteAugmentedValidator):
        """
        Add an attribute to the chain of attributes to load.
        """
        self._attrs.append(item)
        return self


# Define the LOAD_ operators.
LOAD_FAST = _LoadOPSuper(tokens.LOAD_FAST, "varnames")
LOAD_CONST = _LoadOPSuper(tokens.LOAD_CONST, "consts")
LOAD_ATTR = _LoadOPSuper(tokens.LOAD_ATTR, "names")
LOAD_GLOBAL = _LoadOPSuper(tokens.LOAD_GLOBAL, "names")
