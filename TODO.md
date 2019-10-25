# TODO

## Views

Views are mutable slices of compound data types. They isolate a
subset of data from a dict, set, or list and provide real-time access to the
data structure. There are 3 types of Views:

- `DictView`
- `SetView`
- `ListView`

For example, a `DictView` might work like this:

```python
>>> d = dict(a=1, b=2, c=3, d=4, e=5)
>>> view = DictView(d, keys=('a', 'b', 'e'))
>>> view['b']
2
>>> d['b'] = 30
>>> view['b']
30
>>> view['a'] = 15
>>> d['a']
15
>>> del view['a']
>>> d
{'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

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