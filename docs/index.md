# Pyte

*Pyte* is a bytecode creator and compiler for Python >3.2 that allows you to generate safe and fast bytecode for the
Python interpreter in an object-oriented way.  

Python bytecode is hard to get correct. The CPython version of the interpreter will segfault on any code that it
doesn't like, making writing it by hand a tedious and risky process. Pyte allows you to generate this code
automatically using simple objects, enforcing safety of your code to prevent any segfaults from happening.

### Contents

 - [Writing your first function](/first-function)
