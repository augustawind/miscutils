"""nested - tools for fetching and modifying deeply nested attributes

This module exports three functions and some accompanying Exception classes.
It's overall purpose is to facillitate working with deeply nested attributes
on various types of objects in an easy way.

API
---

* ``get(obj, path)`` retrieves a nested value.
* ``set(obj, path, value)`` replaces a nested value with a new value.
* ``update(obj, path, transform)`` calls a function on a nested value and
    sets it to the return value.

The ``path`` parameter on each function takes a string which specifies how to
reach the desired value. This mini-DSL is described below.

Path DSL
--------

The syntax of the path DSL is:

```python
path            ::=  operation [operation [operation ...]]
operation       ::=  lhs_operator parameter [rhs_operator]
lhs_operator    ::=  "." | "[" | "#"
rhs_operator    ::=  "]"
parameter       ::=  string
```

A ``path`` is just a sequence of alternating operators and parameters, where
each operator describe how to access each parameter. These pairs form a
sequence of instructions. When you call a function in this module, each
instruction is executed on the result of the previous instruction until the
instructions are exhausted. The first instruction is executed on the object
passed to the function, the second is executed on the result of that
instruction, and so on, returning the final value.

The available operations are:

============  =============================  =========  ===============
Name          Syntax                         Parameter  Python executed
============  =============================  =========  ===============
attr          `"." parameter`                string     `getattr(obj, param)`
key           `"[" parameter "]"`            string     `obj[param]`
index         `"#" parameter`                integer    `obj[param]`
============  =============================  =========  ===============

Examples:

```python
>>> from utils import nested
>>> obj = [None, {'foo': type('T', (object,), {'x': 8, 'y': -2})}]
>>> nested.get(obj, '#0')
None
>>> nested.get(obj, '#2[foo]')
<class '__main__.T'>
>>> nested.get(obj, '#2[foo].y')
-2
```
"""
from collections import OrderedDict, namedtuple
from enum import Enum

__all__ = ['get', 'MissingCloseOperator', 'MissingOpenOperator',
          'MissingValueChar', 'UnexpectedCloseOperator']

Operation = Enum('Operation', 'ATTR KEY INDEX')
Instruction = namedtuple('Instruction', 'item operation')

LHS_OPS = OrderedDict((
    ('.', Operation.ATTR),
    ('[', Operation.KEY),
    ('#', Operation.INDEX),
))
RHS_OPS = OrderedDict((
    (Operation.KEY, ']'),
))
OP_CHARS = [
    *LHS_OPS.keys(),
    *RHS_OPS.values(),
]


class Error(Exception):
    """Base class for errors in this module."""


class MissingCloseOperator(Error):

    def __init__(self, op, char):
        super().__init__(
            f"missing rhs operator: operation started with char '{char}':"
            f" expected rhs op char '{RHS_OPS[op]}'")


class MissingOpenOperator(Error):

    lhs_ops_repr = ' , '.join(f"'{char}'" for char in LHS_OPS.keys())

    def __init__(self, char):
        super().__init__(
            f"missing lhs operator: expected an lhs operator char"
            f" but found '{char}' (must be one of: {self.lhs_ops_repr})")


class MissingValueChar(Error):

    def __init__(self, op):
        op_char = [char for char, operator in LHS_OPS.items()
                   if op is operator][0]
        super().__init__(f"missing value after lhs operator `{op_char}`")


class UnexpectedCloseOperator(Error):

    def __init__(self, char):
        super().__init__(f"unexpected rhs operator `{char}`")


def parse_instructions(path):
    """Attempt to parse a string into instructions for modifying an object."""
    instructions = []
    operation = None
    item = ''

    for char in path:
        # Grab the operator if this char is an lhs operator char
        lhs_op = LHS_OPS.get(char)

        if operation is None:
            # If no current operation, assert that char is an lhs operator
            if not lhs_op:
                raise MissingOpenOperator(char)
            # Assign the new operator
            operation = lhs_op
        else:
            # If char is not an operator char, append it to current value
            if char not in OP_CHARS:
                item += char
                continue

            # Otherwise, translate current op into instruction
            instructions.append(Instruction(item, operation))
            item = ''

            # If the current op expects a rhs op char...
            rhs_op_char = RHS_OPS.get(operation)
            if rhs_op_char:
                # ...raise error if the current char is an lhs op char
                if lhs_op:
                    raise MissingCloseOperator(operation, char)
                # ...clear current op if current char is the rhs op char
                if char == rhs_op_char:
                    operation = None
                continue

            # Else if the current op has no rhs op char...
            if lhs_op:
                # ...if current char is an lhs op char, start new operation
                operation = lhs_op
            else:
                # ...otherwise it's a misplaced rhs op char, so raise error
                raise UnexpectedCloseOperator(char)

    # Process final operation if it had no rhs op char
    if operation is not None:
        # Raise an error if no value was present
        if not item:
            raise MissingValueChar(operation)

        # Raise an error if op expects a rhs op char
        if operation in RHS_OPS:
            for char, op in LHS_OPS.items():
                if op is operation:
                    raise MissingCloseOperator(operation, char)

        # Translate final operation into instruction
        instructions.append(Instruction(item, operation))

    return instructions


def get(value, path):
    """Fetch an arbitrarily nested value from the given object."""
    instructions = parse_instructions(path)
    for instruction in instructions:
        if instruction.operation is Operation.ATTR:
            value = getattr(value, instruction.item)
        elif instruction.operation is Operation.KEY:
            value = value[instruction.item]
        elif instruction.operation is Operation.INDEX:
            value = value[int(instruction.item)]
        else:
            raise ValueError("PROGRAM ERROR: unexpected operation"
                             f" `{instruction.operation}`")
    return value
