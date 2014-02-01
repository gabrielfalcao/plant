# String operations on a Node


A node has many handy properties and methods, you can get the relative path to a certain file, get the base name, and some other sweets:

```python
>>> from plant import Node
>>>
>>> unit_test_file = Node("tests/unit/test_base.py")
>>> unit_test_file.basename
u'test_base.py'
>>> unit_test_file.path  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
u'/.../tests/unit/test_base.py'
```


## Aso works with directories

```python
>>> from plant import Node
>>>
>>> unit_test_file = Node("tests/unit/test_base.py")
>>> unit_test_file.dir.basename
u'unit'
```
