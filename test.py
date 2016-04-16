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
func = pyte.compile(bc, consts, names, varnames)

print(dis.code_info(func))
print(func.__code__.co_code)
dis.dis(func)

time.sleep(0.05)

a = func()

