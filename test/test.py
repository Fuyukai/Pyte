import pyte

# Create a new consts value.
consts = pyte.create_validated("Hello, world!")
# New varnames values
varnames = pyte.create_validated()

bc = [pyte.load.LOAD_CONST(consts[0]),
      pyte.tokens.RETURN_VALUE]

# Compile the code.
func = pyte.compile(bc, consts, varnames)

# Call it.
a = func()
print(a)
