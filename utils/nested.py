from collections import OrderedDict, namedtuple
from enum import Enum

__all__ = ['get', 'MissingCloseOperator', 'MissingOpenOperator',
          'MissingValueChar', 'UnexpectedCloseOperator']

Operation = Enum('Operation', 'ATTR KEY INDEX')
Instruction = namedtuple('Instruction', 'item operation')

OPEN_OPS = OrderedDict((
    ('.', Operation.ATTR),
    ('[', Operation.KEY),
    ('#', Operation.INDEX),
))
CLOSE_OPS = OrderedDict((
    (Operation.KEY, ']'),
))
OP_CHARS = [
    *OPEN_OPS.keys(),
    *CLOSE_OPS.values(),
]


class Error(Exception):
    """Base class for errors in this module."""


class MissingCloseOperator(Error):

    def __init__(self, op, char):
        super().__init__(
            f"missing close operator: operation started with char '{char}':"
            f" expected closing char '{CLOSE_OPS[op]}'")


class MissingOpenOperator(Error):

    open_ops_repr = ' , '.join(f"'{char}'" for char in OPEN_OPS.keys())

    def __init__(self, char):
        super().__init__(
            f"missing open operator: expected an open operator char"
            f" but found '{char}' (must be one of: {self.open_ops_repr})")


class MissingValueChar(Error):

    def __init__(self, op):
        op_char = [char for char, operator in OPEN_OPS.items()
                   if op is operator][0]
        super().__init__(f"missing value after open operator `{op_char}`")


class UnexpectedCloseOperator(Error):

    def __init__(self, char):
        super().__init__(f"unexpected close operator `{char}`")


def parse_instructions(path):
    """Attempt to parse a string into instructions for modifying an object."""
    instructions = []
    operation = None
    item = ''

    for char in path:
        # Grab the operator if this char is an open operator char
        open_op = OPEN_OPS.get(char)

        if operation is None:
            # If no current operation, assert that char is an open operator
            if not open_op:
                raise MissingOpenOperator(char)
            # Assign the new operator
            operation = open_op
        else:
            # If char is not an operator char, append it to current value
            if char not in OP_CHARS:
                item += char
                continue

            # Otherwise, translate current op into instruction
            instructions.append(Instruction(item, operation))
            item = ''

            # If the current op expects a closing char...
            close_op_char = CLOSE_OPS.get(operation)
            if close_op_char:
                # ...raise error if the current char is an open op char
                if open_op:
                    raise MissingCloseOperator(operation, char)
                # ...clear current op if current char is the closing char
                if char == close_op_char:
                    operation = None
                continue

            # Else if the current op has no closing char...
            if open_op:
                # ...if current char is an open op char, start new operation
                operation = open_op
            else:
                # ...otherwise it's a misplaced close op char, so raise error
                raise UnexpectedCloseOperator(char)

    # Process final operation if it had no closing char
    if operation is not None:
        # Raise an error if no value was present
        if not item:
            raise MissingValueChar(operation)

        # Raise an error if op expects a closing char
        if operation in CLOSE_OPS:
            for char, op in OPEN_OPS.items():
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
