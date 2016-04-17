import dis
import time

import pyte

# Create a new consts value.
consts = pyte.create_consts(None, 1, 2, 3, 6, "Equal!")
# New varnames values
varnames = pyte.create_varnames()
# Create names (for globals)
names = pyte.create_names("print")

bc = [
    pyte.ops.IF(
        conditions=[consts[1] + consts[2] + consts[3] == consts[4]],
        body=[[pyte.ops.CALL_FUNCTION(names[0], consts[5])]]
    ),
    pyte.ops.END_FUNCTION(consts[0])
]

# Compile the code.
func = pyte.compile(bc, consts, names, varnames, stack_size=99)

print("==================================================")
print(dis.code_info(func))
print("\nFunction disassembly: ")
dis.dis(func)

print("\n==================================================\n")

time.sleep(0.05)

a = func()

