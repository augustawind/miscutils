from collections import OrderedDict, namedtuple
from enum import Enum

Operation = Enum('Operation', 'ATTR KEY INDEX')
Instruction = namedtuple('Instruction', 'item operation')

OP_STARTS = OrderedDict((
    ('.', Operation.ATTR),
    ('[', Operation.KEY),
    ('#', Operation.INDEX),
))
OP_ENDS = {
    Operation.KEY: [']'],
}
OP_CHARS = [
    *OP_STARTS.keys(),
    *(v for value in OP_ENDS.values() for v in value)
]

OPS_REPR = ' , '.join(f"'{char}'" for char in OP_STARTS.keys())


class UnfinishedOperation(ValueError):

    def __init__(self, op, char):
        super().__init__(
            f"unfinished `{op.name}` operation started with char '{char}';"
            f" expected closing char '{OP_ENDS[op]}'")


def _parse(path):
    instructions = []
    operation = None
    item = ''

    for char in path:
        new_op = OP_STARTS.get(char)
        if operation is None:
            if new_op:
                operation = new_op
            else:
                raise ValueError(
                    f"expected an operator ({OPS_REPR}) but got '{char}'")
        else:
            if char not in OP_CHARS:
                item += char
                continue

            instructions.append(Instruction(item, operation))
            item = ''

            if char in OP_ENDS.get(operation, ()):
                if new_op:
                    raise UnfinishedOperation(operation, char)
                operation = None
            elif new_op:
                operation = new_op

    if operation is not None:
        if operation in OP_ENDS:
            for char, op in OP_STARTS.items():
                if op is operation:
                    break
            raise UnfinishedOperation(op, char)

        instructions.append(Instruction(item, operation))

    return instructions


def get(value, path):
    instructions = _parse(path)
    for instruction in instructions:
        if instruction.operation is Operation.ATTR:
            value = getattr(value, instruction.item)
        elif instruction.operation is Operation.KEY:
            value = value[instruction.item]
        elif instruction.operation is Operation.INDEX:
            value = value[int(instruction.item)]
        else:
            raise ValueError(f'unexpected operation `{instruction.operation}`')
    return value
