"""
BUILD_ tokens.
"""
import types

import pyte
from pyte import tokens, util
from pyte.exc import ValidationError
from pyte.superclasses import _PyteAugmentedValidator, _PyteOp
from pyte.util import PY36, ensure_instruction


class _Builder(_PyteOp):
    def __init__(self, *args, store: _PyteAugmentedValidator = None):
        super().__init__(*args)

        if store:
            self._to_store = store
        else:
            self._to_store = None

    def _to_bytes_basic(self, previous: bytes):
        bc = b""
        self.args = list(util.flatten(self.args))
        for arg in self.args:
            bytecode = util.generate_bytecode_from_obb(arg, previous)
            bc += bytecode
        return bc

    def _should_store(self):
        if self._to_store:
            # If we should store, store it.
            if not isinstance(self._to_store, _PyteAugmentedValidator):
                raise ValidationError("Cannot save built structure to item of type `{}`"
                                      .format(type(self._to_store)))
            else:
                # Validate it
                self._to_store.validate()
                return util.generate_simple_call(tokens.STORE_FAST, self._to_store.index)
        else:
            return b""


class _BuildList(_Builder):
    def to_bytes(self, previous: bytes):
        # to_bytes methods in these are very simple.
        # they simply concat the inner body.
        # then add the appropriate token.
        bc = self._to_bytes_basic(previous)
        # Add a BUILD_LIST instruction
        bc += tokens.BUILD_LIST.to_bytes(1, byteorder="little")
        # TODO: Extended args for Py3.6+
        if PY36:
            bc += len(list(self.args)).to_bytes(1, byteorder="little")
        else:
            bc += len(list(self.args)).to_bytes(2, byteorder="little")
        # If we should store, add a STORE_FAST instruction
        bc += self._should_store()
        return bc


class _BuildTuple(_Builder):
    def to_bytes(self, previous: bytes):
        bc = self._to_bytes_basic(previous)
        # Add a BUILD_TUPLE instruction
        bc += tokens.BUILD_TUPLE.to_bytes(1, byteorder="little")
        if PY36:
            bc += len(list(self.args)).to_bytes(1, byteorder="little")
        else:
            bc += len(list(self.args)).to_bytes(2, byteorder="little")
        # If we should store, add a STORE_FAST instruction
        bc += self._should_store()
        return bc


class _BuildSet(_Builder):
    def __init__(self, *args, store: _PyteAugmentedValidator = None):
        super().__init__(*args, store=store)
        varnames = pyte.create_varnames("self", "previous", "bc")
        consts = pyte.create_consts(1, 2, "little")
        names = pyte.create_names("_to_bytes_basic", "tokens", "BUILD_SET", "to_bytes", "len", "list", "args",
                                  "_should_store")

        instructions = [
            # First, call _to_bytes_basic
            pyte.ops.LOAD_FAST(varnames[0]).attr(names[0]),
            pyte.ops.CALL_FUNCTION(None, varnames[1]),
            # Load tokens.MAP.to_bytes
            pyte.ops.LOAD_GLOBAL(names[1]).attr(names[2]).attr(names[3]),
            # Call to_bytes on BUILD_SET
            pyte.ops.CALL_FUNCTION(None, consts[0], consts[2]),
            # Add it together.
            ensure_instruction(pyte.tokens.BINARY_ADD),
            # Add the len(list(self.args))
            pyte.ops.LOAD_GLOBAL(names[4]),
            pyte.ops.LOAD_GLOBAL(names[5]),
            # Call list(self.args)
            pyte.ops.LOAD_FAST(varnames[0]).attr(names[6]),
            pyte.ops.CALL_SIMPLE(1),
            # Call len(^)
            pyte.ops.CALL_SIMPLE(1),
            # Call .to_bytes
            pyte.ops.LOAD_ATTR(names[3]),
            pyte.ops.CALL_FUNCTION(None, consts[1], consts[2]),
            # Add it to bc
            ensure_instruction(pyte.tokens.BINARY_ADD),
            # Return
            pyte.tokens.RETURN_VALUE
        ]

        func = pyte.compile(instructions, consts=consts, varnames=varnames, names=names,
                            arg_count=2, func_name="to_bytes")

        self.to_bytes = types.MethodType(func, self)


# Bytecode version of _BuildSet

LIST = _BuildList
TUPLE = _BuildTuple
SET = _BuildSet
