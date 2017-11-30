"""nested - tools for working with arbitrarily nested data structures

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
path            ::=  accessor [accessor [accessor ...]]
accessor        ::=  lhs_operator parameter [rhs_operator]
lhs_operator    ::=  "." | "[" | "#"
rhs_operator    ::=  "]"
parameter       ::=  string
```

A ``path`` is just a sequence of alternating operators and parameters, where
each operator describe how to access each parameter. These pairs form a
sequence of actions. When you call a function in this module, each action is
executed on the result of the previous action until the actions are exhausted.
The first action is executed on the object passed to the function, the second
is executed on the result of that action, and so on, returning the final value.

The available accessors are:

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
from operator import getitem, setitem

__all__ = ['get', 'set', 'update', 'DataNode', 'MissingRHSOperator',
           'MissingLHSOperator', 'UnexpectedRHSOperator', 'MissingValueChar']

DataNode = namedtuple('DataNode', 'value action parent')

Action = namedtuple('Action', 'item accessor')

Accessor = Enum('Accessor', 'ATTR KEY INDEX')

LHS_OPS = OrderedDict((
    ('.', Accessor.ATTR),
    ('[', Accessor.KEY),
    ('#', Accessor.INDEX),
))
RHS_OPS = OrderedDict((
    (Accessor.KEY, ']'),
))

OP_CHARS = [
    *LHS_OPS.keys(),
    *RHS_OPS.values(),
]


def get(data, path):
    """Fetch the value of an arbitrarily nested property.

    Args:
        data: Compound data structure to traverse.
            It must support attribute access (`__getattribute__`) or item
            access (`__getitem__`).
        path (str): Path to the target property in ``data``.
        value: The value to write to the target property.

    Returns:
        The value of the target property.
    """
    return get_with_context(data, path).value


def set(data, path, value):
    """Set the value of an arbitrarily nested property.

    Args:
        data: Compound data structure to traverse.
            Must be mutable. Must support attribute access (`__getattribute__`)
            or item access (`__getitem__`).
        path (str): Path to the target property in ``data``.
        value: The value to write to the target property.

    Returns:
        The modified ``data`` object. Since this function mutates ``data``, the
        return value is not meaningful and is simply a convenience to allow
        method chaining.
    """
    node = get_with_context(data, path)
    put(node.parent, node.action, value)
    return data


def update(data, path, transform):
    """Transform the value of an arbitrarily nested property.

    Args:
        data: Compound data structure to traverse.
            Must be mutable. Must support attribute access (`__getattribute__`)
            or item access (`__getitem__`).
        path (str): Path to the target value in ``data``.
        transform (callable): Callable that transforms the target value.
            It should take a ``DataNode`` instance as its sole argument. Its
            return value will replace the target value in ``data``.

    Returns:
        The modified ``data`` object. Since this function mutates ``data``, the
        return value is not meaningful and is simply a convenience to allow
        method chaining.
    """
    node = get_with_context(data, path)
    value = transform(node)
    put(node.parent, node.action, value)
    return data


def get_with_context(data, path):
    actions = parse_actions(path)
    for action in actions:
        parent = data
        data = pick(data, action)
    return DataNode(
        value=data,
        action=action,
        parent=parent,
    )


def pick(data, action):
    if action.accessor is Accessor.ATTR:
        return getattr(data, action.item)
    elif action.accessor is Accessor.KEY:
        return data[action.item]
    elif action.accessor is Accessor.INDEX:
        return data[int(action.item)]
    else:
        raise ValueError("PROGRAM ERROR: unexpected accessor"
                         f" `{action.accessor}`")


def put(data, action, value):
    if action.accessor is Accessor.ATTR:
        setattr(data, action.item, value)
    elif action.accessor is Accessor.KEY:
        data[action.item] = value
    elif action.accessor is Accessor.INDEX:
        data[int(action.item)] = value
    else:
        raise ValueError("PROGRAM ERROR: unexpected accessor"
                         f" `{action.accessor}`")


def parse_actions(path):
    """Attempt to parse a string into actions for modifying an object."""
    actions = []
    accessor = None
    item = ''

    for char in path:
        # Grab the operator if this char is an lhs operator char
        lhs_op = LHS_OPS.get(char)

        if accessor is None:
            # If no current accessor, assert that char is an lhs operator
            if not lhs_op:
                raise MissingLHSOperator(char)
            # Assign the new operator
            accessor = lhs_op
        else:
            # If char is not an operator char, append it to current value
            if char not in OP_CHARS:
                item += char
                continue

            # Otherwise, translate current op into action
            actions.append(Action(item, accessor))
            item = ''

            # If the current op expects a rhs op char...
            rhs_op_char = RHS_OPS.get(accessor)
            if rhs_op_char:
                # ...raise error if the current char is an lhs op char
                if lhs_op:
                    raise MissingRHSOperator(accessor, char)
                # ...clear current op if current char is the rhs op char
                if char == rhs_op_char:
                    accessor = None
                continue

            # Else if the current op has no rhs op char...
            if lhs_op:
                # ...if current char is an lhs op char, start new accessor
                accessor = lhs_op
            else:
                # ...otherwise it's a misplaced rhs op char, so raise error
                raise UnexpectedRHSOperator(char)

    # Process final accessor if it had no rhs op char
    if accessor is not None:
        # Raise an error if no value was present
        if not item:
            raise MissingValueChar(accessor)

        # Raise an error if op expects a rhs op char
        if accessor in RHS_OPS:
            for char, op in LHS_OPS.items():
                if op is accessor:
                    raise MissingRHSOperator(accessor, char)

        # Translate final accessor into action
        actions.append(Action(item, accessor))

    return actions


class Error(Exception):
    """Base class for errors in this module."""


class MissingRHSOperator(Error):

    def __init__(self, op, char):
        super().__init__(
            f"missing rhs operator: accessor started with char '{char}':"
            f" expected rhs op char '{RHS_OPS[op]}'")


class MissingLHSOperator(Error):

    lhs_ops_repr = ' , '.join(f"'{char}'" for char in LHS_OPS.keys())

    def __init__(self, char):
        super().__init__(
            f"missing lhs operator: expected an lhs operator char"
            f" but found '{char}' (must be one of: {self.lhs_ops_repr})")


class UnexpectedRHSOperator(Error):

    def __init__(self, char):
        super().__init__(f"unexpected rhs operator `{char}`")


class MissingValueChar(Error):

    def __init__(self, op):
        op_char = [char for char, operator in LHS_OPS.items()
                   if op is operator][0]
        super().__init__(f"missing value after lhs operator `{op_char}`")
