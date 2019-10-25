import itertools
from collections.abc import Mapping


def merge(*args: Mapping, _depth: int = 0, **kwargs) -> Mapping:
    """Compose one or more mappings with kwargs.

    If ``args`` are given, the first is used as the base mapping. Otherwise,
    the base is a new dict. Remaining args are merged into the base in
    sequence, overriding previous keys. ``kwargs`` is treated as another
    mapping and merged in last. The result is returned whether a new mapping
    was created or not.

    Args:
        *args: Mappings to merge.
        _depth (int): The depth to merge nested mappings.
        **kwargs: Key/value pairs.

    Returns:
        (Mapping) The modified mapping. This is either the first positional
        argument passed to merge or a new dict if no positional args were
        given. If it's the former and you have a reference to it you can
        probably ignore the return value.
    """
    if not args:
        args.append({})
    base = args[0]
    for arg in itertools.chain(args[1:], (kwargs,)):
        if not arg:
            continue
        for key, val in arg.items():
            if _depth != 0 and isinstance(val, Mapping):
                base_val = base.get(key)
                if isinstance(base_val, Mapping):
                    base[key] = merge(base_val, val, _depth=_depth - 1)
                    continue
            base[key] = val
    return base
