"""
Superclasses for various Pyte things.
"""
import dis
import functools

from pyte import tokens, util
from pyte.exc import ValidationError
from pyte.util import PY36

BIN_OP_MAP = {}

for num, val in enumerate(dis.cmp_op):
    BIN_OP_MAP[val] = num


class _PyteOp(object):
    """
    This is a superclass for an opcode object, I.E an operation like `LOAD_FAST`.
    """

    def __init__(self, *args):
        # Generic init
        self.args = args

    # How wide this operation is (in bytes)
    op_width = 0

    def to_bytes(self, previous: bytes) -> bytes:
        """
        Produces a byte string representing the `co_code` of this operator.
        """
        raise NotImplementedError


class _PyteAugmentedComparator(object):
    """
    An augmented comparator is used for the IF statements, in order to generate the correct 
    bytecode.
    """

    def __init__(self, opcode: int, first, second):
        self.opcode = opcode
        self.first = first
        self.second = second

    def to_bytes(self, previous):
        return self.to_bytecode(previous)

    def to_bytecode(self, previous):
        bc = b""
        # Generate LOAD_
        for val in [self.first, self.second]:
            if isinstance(val, _PyteOp):
                # Mathematical ops
                bc += val.to_bytes(previous + bc)
                continue
            if val.list_name == "consts":
                bc += util.generate_load_const(val.index)
            elif val.list_name == "names":
                bc += util.generate_load_global(val.index)
            elif val.list_name == "varnames":
                bc += util.generate_load_fast(val.index)
        # Add the CMP_OP
        bc += tokens.COMPARE_OP.to_bytes(1, byteorder="little")
        # Add the operator
        # In Py 3.6+ the operator is only one byte.
        if PY36:
            bc += self.opcode.to_bytes(1, byteorder="little")
        else:
            bc += self.opcode.to_bytes(2, byteorder="little")
        return bc


class _FakeMathematicalOP(_PyteOp):
    """
    Represents a fake mathematical operation. These are returned from mathematical operations on 
    Pyte objects, and can be used to create bytes from them automatically.
    """

    def __init__(self, *args, opcode: int = None):
        super().__init__(*args)
        if opcode is None:
            # what
            raise ValidationError("This should never happen")
        self.opcode = opcode

    def to_bytes(self, previous: bytes):
        bc = b""
        # Add together all of the args.
        for index, arg in enumerate(self.args):
            # Validate the arg.
            arg.validate()
            # Get the LOAD_ call.
            bc += arg.to_load()
            # Add a BINARY_* depending on if we are the first argument, or any more arguments.
            if index != 0:
                size = 1
                if PY36:
                    # py36 change: binary operators are now 2 bytes wide
                    size = 2
                bc += self.opcode.to_bytes(size, byteorder="little")
        return bc

    def __append_args(self, other):
        if other.__class__.__name__ == "_PyteAugmentedValidator":
            tmp_args = list(self.args)
            tmp_args.append(other)
            self.args = tuple(tmp_args)
        else:
            self.args = tuple(list(self.args) + list(other.args))
        return self

    def __add__(self, other):
        if self.opcode != tokens.BINARY_ADD:
            raise ValueError("Cannot add in non-add mode.")
        return self.__append_args(other)

    def __sub__(self, other):
        if self.opcode != tokens.BINARY_SUBTRACT:
            raise ValueError("Cannot subtract in non-sub mode.")
        return self.__append_args(other)

    def __mul__(self, other):
        if self.opcode != tokens.BINARY_MULTIPLY:
            raise ValueError("Cannot multiply in non-mul mode.")
        return self.__append_args(other)

    def __truediv__(self, other):
        if self.opcode != tokens.BINARY_TRUE_DIVIDE:
            raise ValueError("Cannot truediv in non-truediv mode.")
        return self.__append_args(other)

    def __floordiv__(self, other):
        if self.opcode != tokens.BINARY_FLOOR_DIVIDE:
            raise ValueError("Cannot floordiv in non-floordiv mode.")
        return self.__append_args(other)


class _PyteAugmentedValidator(object):
    """
    An augmented validator ensures that the bytecode objects do not segfault when the bytecode is 
    compiled and ran,
    by validating the arguments.
    """

    def __init__(self, index, get_partial, name):
        self.index = index
        self.partial = get_partial
        self._l_name = name

    def to_load(self):
        if self._l_name == "consts":
            return util.generate_load_const(self.index)
        elif self._l_name == "varnames":
            return util.generate_load_fast(self.index)
        elif self._l_name == "names":
            return util.generate_load_global(self.index)

    @property
    def list_name(self):
        return self._l_name

    def validate(self):
        try:
            return self.partial()
        except IndexError:
            raise ValidationError("Index `{}` does not exist at compile-time".format(self.index))

    def get(self):
        return self.validate()

    # Magic methods for maths stuff
    def __add__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_ADD)

    def __sub__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_SUBTRACT)

    def __mul__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_MULTIPLY)

    def __floordiv__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_FLOOR_DIVIDE)

    def __truediv__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_TRUE_DIVIDE)

    def __mod__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_MODULO)

    # Bitwise
    def __and__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_AND)

    def __or__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_OR)

    def __lshift__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_LSHIFT)

    def __rshift__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_RSHIFT)

    def __xor__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_XOR)

    # 3.5 matrix multiple

    def __matmul__(self, other):
        return _FakeMathematicalOP(self, other, opcode=tokens.BINARY_MATRIX_MULTIPLY)

    # Standard comparison ops

    def __eq__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP["=="], self, other)

    def __ne__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP["!="], self, other)

    def __gt__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP[">"], self, other)

    def __lt__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP["<"], self, other)

    def __ge__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP[">="], self, other)

    def __le__(self, other):
        return _PyteAugmentedComparator(BIN_OP_MAP["<="], self, other)


class PyteAugmentedArgList(list):
    """
    This is a superclass for an augmented argument list.

    This is not actually subclassed, but used directly in an alias.

    Instead of providing items to use, it provides validators that are validated in `compile`.
    """

    def __init__(self, *args, name: str = "consts"):
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
