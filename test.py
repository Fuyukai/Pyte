import dis
import time

import pyte

# Create a new consts value.
consts = pyte.create_consts(None, "Hello, world!")
# New varnames values
varnames = pyte.create_varnames()
# Create names (for globals)
names = pyte.create_names("print")

bc = [pyte.call.CALL_FUNCTION(names[0], consts[1]),
      pyte.tokens.RETURN_VALUE]

# Compile the code.
func = pyte.compile(bc, consts, names, varnames, stack_size=99)

print("==================================================")
print(dis.code_info(func))
print("\nFunction disassembly: ")
dis.dis(func)

print("\n==================================================\n")

time.sleep(0.05)

a = func()

