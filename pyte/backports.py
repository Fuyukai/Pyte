import collections, dis, sys

_Instruction = collections.namedtuple("_Instruction",
                                      "opname opcode arg argval argrepr offset starts_line is_jump_target")


class Instruction(_Instruction):
    """Details for a bytecode operation

       Defined fields:
         opname - human readable name for operation
         opcode - numeric code for operation
         arg - numeric argument to operation (if any), otherwise None
         argval - resolved arg value (if known), otherwise same as arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (if any), otherwise None
         is_jump_target - True if other code jumps to here, otherwise False
    """

    def _disassemble(self, lineno_width=3, mark_as_current=False):
        """Format instruction details for inclusion in disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow as part of the line
        """
        fields = []
        # Column: Source code line number
        if lineno_width:
            if self.starts_line is not None:
                lineno_fmt = "%%%dd" % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(' ' * lineno_width)
        # Column: Current instruction indicator
        if mark_as_current:
            fields.append('-->')
        else:
            fields.append('   ')
        # Column: Jump target marker
        if self.is_jump_target:
            fields.append('>>')
        else:
            fields.append('  ')
        # Column: Instruction offset from start of code sequence
        fields.append(repr(self.offset).rjust(4))
        # Column: Opcode name
        fields.append(self.opname.ljust(20))
        # Column: Opcode argument
        if self.arg is not None:
            fields.append(repr(self.arg).rjust(5))
            # Column: Opcode argument details
            if self.argrepr:
                fields.append('(' + self.argrepr + ')')
        return ' '.join(fields).rstrip()


def _get_instructions_bytes(code, varnames=None, names=None, constants=None,
                            cells=None, linestarts=None, line_offset=0):
    """Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    labels = dis.findlabels(code)
    extended_arg = 0
    starts_line = None
    free = None
    # enumerate() is not an option, since we sometimes process
    # multiple elements on a single pass through the loop
    n = len(code)
    i = 0
    while i < n:
        op = code[i]
        offset = i
        if linestarts is not None:
            starts_line = linestarts.get(i, None)
            if starts_line is not None:
                starts_line += line_offset
        is_jump_target = i in labels
        i = i + 1
        arg = None
        argval = None
        argrepr = ''
        if op >= dis.HAVE_ARGUMENT:
            arg = code[i] + code[i + 1] * 256 + extended_arg
            extended_arg = 0
            i = i + 2
            if op == dis.EXTENDED_ARG:
                extended_arg = arg * 65536
            # Set argval to the dereferenced value of the argument when
            #  availabe, and argrepr to the string representation of argval.
            #    _disassemble_bytes needs the string repr of the
            #    raw name index for LOAD_GLOBAL, LOAD_CONST, etc.
            argval = arg
            if op in dis.hasconst:
                argval, argrepr = dis._get_const_info(arg, constants)
            elif op in dis.hasname:
                argval, argrepr = dis._get_name_info(arg, names)
            elif op in dis.hasjrel:
                argval = i + arg
                argrepr = "to " + repr(argval)
            elif op in dis.haslocal:
                argval, argrepr = dis._get_name_info(arg, varnames)
            elif op in dis.hascompare:
                argval = dis.cmp_op[arg]
                argrepr = argval
            elif op in dis.hasfree:
                argval, argrepr = dis._get_name_info(arg, cells)
            elif op in dis.hasnargs:
                argrepr = "%d positional, %d keyword pair" % (code[i - 2], code[i - 1])
        yield dis.Instruction(dis.opname[op], op,
                              arg, argval, argrepr,
                              offset, starts_line, is_jump_target)


def apply():
    dis._get_instructions_bytes = _get_instructions_bytes
    dis.Instruction = Instruction
