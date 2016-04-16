"""
Superclasses for various Pyte things.
"""
import functools

from pyte.exc import ValidationError


class _PyteOp(object):
    """
    This is a superclass for an opcode object, I.E an operation like `LOAD_FAST`.
    """

    # How wide this operation is (in bytes)
    op_width = 0

    def to_bytes(self) -> bytes:
        """
        Produces a byte string representing the `co_code` of this operator.
        """
        raise NotImplementedError


class _PyteAugmentedValidator(object):
    """
    An augmented validator ensures that the bytecode objects do not segfault when the bytecode is compiled and ran,
    by validating the arguments.
    """
    def __init__(self, index, get_partial, name):
        self.index = index
        self.partial = get_partial
        self._l_name = name

    @property
    def list_name(self):
        return self._l_name

    def get(self):
        try:
            return self.partial()
        except IndexError as e:
            raise ValidationError("Index `{}` does not exist at runtime".format(self.index)) from None


class PyteAugmentedArgList(list):
    """
    This is a superclass for an augmented argument list.

    This is not actually subclassed, but used directly in an alias.

    Instead of providing items to use, it provides validators that are validated in `compile`.
    """
    def __init__(self, *args, name: str="consts"):
        super().__init__(*args)
        self.name = name

    def all(self):
        """
        Return all values of self.
        """
        return [x for x in self]

    def __getitem__(self, item):
        # Create a partial to get the list item.
        part = functools.partial(super().__getitem__, item)
        # Return a new _PyteAugmentedValidator.
        return _PyteAugmentedValidator(item, part, self.name)

