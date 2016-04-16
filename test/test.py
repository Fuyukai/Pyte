import pyte

bc = [pyte.tokens.LOAD_CONST, 0, 0,
      pyte.tokens.RETURN_VALUE]

func = pyte.compile(bc, ["Hello, world!"], [])

print(func.__code__.co_code)

a = func()
print(a)