"""
IF operands.
This is horrible code, that detects jumps.
You have been warned.
"""
from pyte import exc, tokens
from pyte import compiler
from pyte.superclasses import _PyteOp, _PyteAugmentedValidator
from pyte.util import generate_simple_call


class IF(_PyteOp):
    """
    An IF operator is Pyte's implementation of the `if elif else` syntax.

    This uses a slightly convoluted syntax to define the IF/ELSE, and set up the appropriate jumps.
    """

    def __init__(self, conditions: list, body: list):
        """
        Create a new IF operator.

        Parameters:

            conditions: list
                Conditions is a list of conditions to check the IF statement for.
                These can be wrapped in a :class:`pyte.superclasses.PyteOr`/:class:`pyte.superclasses.PyteAnd` if you
                wish to have multiple conditions for one block.

                Conditions can be created using the standard truth operators (<, >, >=, <=, ==, !=). If there is only
                one condition to check (i.e a truthy check) that will be evaluated to generate the bytecode.

            body: list
                This should be a LIST OF LISTS. There should be as many lists as there are conditions to check. If
                there are not, a CompileError will be raised.

                These lists are standard lists of instructions for the Pyte compiler.
        """

        self.conditions = conditions
        self.body = body

    def to_bytes(self, previous: bytes):
        """
        Complex code ahead. Comments have been added in as needed.
        """
        # First, validate the lengths.
        if len(self.conditions) != len(self.body):
            raise exc.CompileError("Conditions and body length mismatch!")

        bc = b""

        prev_len = len(previous)

        # Loop over the conditions and bodies
        for condition, body in zip(self.conditions, self.body):
            # Generate the conditional data.
            cond_bytecode = condition.to_bytecode(previous)
            bc += cond_bytecode
            # Complex calculation.
            # First, generate the bytecode for all tokens in the body.
            # Then we calculate the len() of that.
            # We create a POP_JUMP_IF_FALSE operation that jumps to the instructions after the body code + 3 for the
            # pop call.
            # This is done for all chained IF calls, as if it was an elif call.
            # Else calls are not possible to be auto-generated, but it is possible to emulate them using an elif
            # call that checks for the opposite of the above IF.

            # Call the _compile_func method from compiler to compile the body.
            body_bc = compiler._compile_bc(body)

            bdyl = len(body_bc)
            # Add together the lengths.
            gen_len = prev_len + len(cond_bytecode) + bdyl + 1
            # Generate the POP_JUMP_IF_FALSE instruction
            bc += generate_simple_call(tokens.POP_JUMP_IF_FALSE, gen_len)
            # Add the body_bc
            bc += body_bc

            # Update previous_len
            prev_len = len(previous) + len(bc)

        return bc
