import pyte

# Create a new consts value.
consts = pyte.create_consts("Hello, world!")
# New varnames values
varnames = pyte.create_varnames()

bc = [pyte.load.LOAD_CONST(consts[0]),
      pyte.tokens.RETURN_VALUE]

# Compile the code.
func = pyte.compile(bc, consts, varnames)

# Call it.
a = func()
print(a)
