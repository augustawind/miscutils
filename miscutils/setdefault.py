from collections import Mapping, MutableSequence, Set
from functools import partial

from .merge import merge


def setdefault(
    value,
    default,
    cls=None,
    merge_lists=False,
    merge_sets=False,
    merge_dicts=False,
    depth=1,
):
    """Transform ``value`` by applying some rules with ``default``.

    The following rules are applied:
        1. If ``value`` is None, return ``default``.
        2. If ``default`` is None, return ``value``.
        3. If ``merge_dicts`` is True, merge mapping types.
        4. If ``merge_lists`` is True, merge mutable sequence types.
        5. If ``merge_sets`` is True, merge set types.

    Args:
        value: The value to be transformed.
        default: The default value.
        cls (type): Desired return type. If possible, the transformed value
            will be returned as an instance of ``cls``. If is omitted or None,
            the return type will be the same as ``value``.
        merge_lists (bool): If ``value`` is a mutable sequence, concatenate
            and return ``default`` + ``value``.
        merge_sets (bool): If ``value`` is a set type, return its union with
            ``default``.
        merge_dicts (bool): If ``value`` is a mapping type, return ``value``
            plus any items from ``default`` whose keys are not in ``value``.
        depth (int): If ``merge_dicts`` is enabled, this sets the max depth
            of nested mappings that will be merged. If -1, no limit will be
            enforced.

    Attributes:
        setdefault.merge_all (function): Run with all merge flags enabled.
        setdefault.merge_dicts (function): Run with `merge_dicts` enabled.
        setdefault.merge_lists (function): Run with `merge_lists` enabled.
        setdefault.merge_sets (function): Run with `merge_sets` enabled.
    """
    value_cls = None

    if value is not None and default is not None:
        value_cls = type(value)
        if merge_dicts:
            value = _setdefault_dict(value, default, depth)
        if merge_lists:
            value = _setdefault_list(value, default)
        if merge_sets:
            value = _setdefault_set(value, default)
        value = value_cls(value)

    elif value is None:
        if default is None:
            return None
        value = default

    if cls:
        return cls(value)
    elif value_cls:
        return value_cls(value)
    return value


def _setdefault_dict(value, default, depth):
    if isinstance(value, Mapping):
        return merge({}, default, value, _depth=depth)
    return value


def _setdefault_set(value, default):
    if isinstance(value, Set):
        return value | default
    return value


def _setdefault_list(value, default):
    if isinstance(value, MutableSequence):
        return [*default, *value]
    return value


def _setdefault_all(value, default, cls=None):
    """Call ``setdefault`` but transform set types and mutable sequences.

    Additional transformations:
    """
    return setdefault(
        value, default, cls, merge_dicts=True, merge_sets=True, merge_lists=True
    )


setdefault.merge_all = _setdefault_all
setdefault.merge_dicts = partial(setdefault, merge_dicts=True)
setdefault.merge_lists = partial(setdefault, merge_lists=True)
setdefault.merge_sets = partial(setdefault, merge_sets=True)
