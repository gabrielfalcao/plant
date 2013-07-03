# Plant - filesystem for humans

[![Build Status](https://secure.travis-ci.org/gabrielfalcao/plant.png?branch=master)](http://travis-ci.org/#!/gabrielfalcao/plant)

[github page](https://github.com/gabrielfalcao/plant)

## Introduction

Plant is a tiny python library that provide handy functions for path
manipulation, file search, and other filesystem-based I/O operations.

It's called plant because you start using an instance of `Node` and
with search operations you start moving through other nodes that
represent paths, they can be folders or files, in fact every possible
path in the disk your software is operating on is a potential "plant"
node. (But it's also given my personal affection towards plants and
vegetables).

## Usage

Here is a quick introduction, but the [full documentation](http://falcao.it/plant) can be found [here](http://falcao.it/plant)
A `Node` takes a path, if it's relative, Plant will turn it into
absolute before storing it internally.

Plant always has the absolute path of the current node.

```python
>>> from plant import Node
>>>
>>> unit_test_folder = Node("tests/unit")
>>> unit_test_folder
<plant.Node (path=tests/unit)>
```

### Getting the parent node

```python
>>> from plant import Node
>>>
>>> unit_test_folder = Node("tests/unit")
>>> unit_test_folder.parent.parent
<plant.Node (path=.)>
```


##
