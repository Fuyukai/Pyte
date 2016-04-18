"""
BUILD_ tokens.
"""
from pyte.exc import ValidationError
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator
from pyte import tokens, util


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
                raise ValidationError("Cannot save built structure to item of type `{}`".format(type(self._to_store)))
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
        bc += len(list(self.args)).to_bytes(2, byteorder="little")
        # If we should store, add a STORE_FAST instruction
        bc += self._should_store()
        return bc


class _BuildTuple(_Builder):
    def to_bytes(self, previous: bytes):
        bc = self._to_bytes_basic(previous)
        # Add a BUILD_TUPLE instruction
        bc += tokens.BUILD_TUPLE.to_bytes(1, byteorder="little")
        bc += len(list(self.args)).to_bytes(2, byteorder="little")
        # If we should store, add a STORE_FAST instruction
        bc += self._should_store()
        return bc

LIST = _BuildList
TUPLE = _BuildTuple
