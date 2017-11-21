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

OPS_REPR = ' , '.join(f"'{char}'" for char in OP_STARTS.keys())


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
            if new_op or char in OP_ENDS.get(operation, ()):
                instructions.append(Instruction(item, operation))
                item = ''
                if new_op:
                    operation = new_op
                else:
                    operation = None
            else:
                item += char

    if operation is not None:
        if operation in OP_ENDS:
            for char, op in OP_STARTS.items():
                if op is operation:
                    break
            raise ValueError(
                f"unfinished `{op.name}` operation started with char '{char}';"
                f" expected closing char '{OP_ENDS[operation]}'")

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
