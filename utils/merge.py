import itertools
from collections import Mapping


def merge(base, *args, _depth=0, **kwargs):
    """Compose one or more mappings with kwargs.

    Args are merged into ``base`` sequentially, each overriding previous keys.
    kwargs are merged in last. If ``base`` is None, a new dict is created. The
    result is returned whether a new mapping was created or not.

    Args:
        base (Mapping): The base mapping.
        *args: Additional mappings.
        _depth (int): The depth to merge nested dicts.
        **kwargs: Key/value paids.

    Returns:
        The ``base`` mapping. If it was None, the newly created mapping is
        returned. Otherwise it's the same mapping that was passed in.
    """
    if base is None:
        base = {}
    for arg in itertools.chain(args, (kwargs,)):
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
