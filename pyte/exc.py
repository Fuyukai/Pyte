"""
Classes for exceptions.
"""


class ValidationError(Exception):
    """
    Raised when something fails to validate.
    """
    pass


class CompileError(Exception):
    """
    Raised when something fails to compile.
    """


class CompileWarning(Warning):
    """
    Represents a warning when compiling.
    """
    pass
