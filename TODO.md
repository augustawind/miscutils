# TODO

## OrderedDict (improved)

An improved version of the stdlib `collections.OrderedDict` that allows
indexing and other list operations.

```python
>>> from miscutils.mappings import OrderedDict
>>> d = OrderedDict(foo=1, bar=2, baz=3)
>>> d.index('baz')
2
>>> d.insert(1, 'quux', 9)
>>> d
OrderedDict({'foo': 1, 'quux': 9, 'bar': 2, 'baz': 3})
>>> d.popitem(1)
('quux', 9)
>>> d.popitem()
('baz', 3)
>>> d
OrderedDict({'foo': 1, 'bar': 2})
```

## OrderedSet

A set that keeps track of the order of insertion. Like `OrderedDict`, but for
sets.