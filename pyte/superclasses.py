"""
Superclasses for various Pyte things.
"""
import functools


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
    def __init__(self, index, get_partial):
        self.index = index
        self.partial = get_partial

    def get(self):
        return self.partial()


class PyteAugmentedArgList(list):
    """
    This is a superclass for an augmented argument list.

    This is not actually subclassed, but used directly in an alias.

    Instead of providing items to use, it provides validators that are validated in `compile`.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        # Create a partial to get the list item.
        part = functools.partial(super().__getitem__, item)
        # Return a new _PyteAugmentedValidator.
        return _PyteAugmentedValidator(item, part)

