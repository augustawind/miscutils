from collections import OrderedDict, namedtuple
from enum import Enum

__all__ = ['get']

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


class UnfinishedOperation(ValueError):

    def __init__(self, op, char):
        super().__init__(
            f"unfinished `{op.name}` operation started with char '{char}';"
            f" expected closing char '{CLOSE_OPS[op]}'")


class MissingOperator(ValueError):

    open_ops_repr = ' , '.join(f"'{char}'" for char in OPEN_OPS.keys())

    def __init__(self, char):
        super().__init__(
            f"missing operator; expected an operator char"
            f" but found '{char}' (must be one of: {self.open_ops_repr})")


def parse_instructions(path):
    instructions = []
    operation = None
    item = ''

    for char in path:
        new_op = OPEN_OPS.get(char)

        if operation is None:
            if new_op:
                operation = new_op
            else:
                raise MissingOperator(char)
        else:
            if char not in OP_CHARS:
                item += char
                continue

            instructions.append(Instruction(item, operation))
            item = ''

            end_op_char = CLOSE_OPS.get(operation)
            if end_op_char:
                if new_op:
                    raise UnfinishedOperation(operation, char)
                if char == end_op_char:
                    operation = None
            elif new_op:
                operation = new_op

    if operation is not None:
        if operation in CLOSE_OPS:
            for char, op in OPEN_OPS.items():
                if op is operation:
                    break
            raise UnfinishedOperation(op, char)

        instructions.append(Instruction(item, operation))

    return instructions


def get(value, path):
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