# Introduction

Plant is a tiny python library that provide handy functions for path
manipulation, file search, and other filesystem-based I/O operations.

It's called plant because you start using an instance of `Node` and
with search operations you start moving through other nodes that
represent paths, they can be folders or files, in fact every possible
path in the disk your software is operating on is a potential "plant"
node. *(Though it's also given my personal affection towards plants and
vegetables)*

## Primer

Here is a quick introduction, but the
[full documentation](http://falcao.it/plant) can be found [here](http://falcao.it/plant)

A `Node` takes a path, if it's
relative, Plant will turn it into absolute before storing it
internally.

Plant always has the absolute path of the current node. (although
below you can see that for debugging purposes the string
representation of a node shows the relative path since the absolute
might be really long.

```python
>>> from plant import Node
>>>
>>> unit_test_folder = Node("tests/unit")
>>> unit_test_folder
<plant.Node (path=tests/unit)>
```
