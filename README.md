# Plant - filesystem for humans

[![Build Status](https://secure.travis-ci.org/gabrielfalcao/plant.png?branch=master)](http://travis-ci.org/#!/gabrielfalcao/plant)
[![Documentation Status](https://readthedocs.org/projects/plant-fs/badge/?version=latest)](http://plant-fs.readthedocs.org/en/latest/?badge=latest)

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


### Finding files by regex


```python
>>> from plant import Node
>>>
>>> test_files = Node("tests").find_with_regex("test_.*.py")
>>> test_files
[<plant.Node (path=tests/functional/test_fs.py)>, <plant.Node (path=tests/unit/test_base.py)>, <plant.Node (path=tests/unit/test_node.py)>]
```

### Every node is a file

And because in unix a directory is a folder, a node might also be a directory.

```python
>>> from plant import Node
>>>
>>> functional_test_file = Node("tests/functional/test_fs.py")
>>> functional_test_file.is_dir
False
>>> functional_test_file.is_file
True
>>> functional_test_file.parent
<plant.Node (path=tests/functional)>
>>> functional_test_file.parent.parent
<plant.Node (path=tests)>
>>> functional_test_file.dir
<plant.Node (path=tests/functional)>
```


### Access the unix stat attributes through metadata

```python
>>> from plant import Node
>>>
>>> test_fs = Node("tests/functional/test_fs.py")
>>> test_fs.metadata.size
3957
>>> test_fs.metadata.keys()
[u'uid', u'dev', u'ctime', u'nlink', u'gid', u'mode', u'mtime', u'atime', u'ino', u'size']
```

[Read the full documentation here](http://falcao.it/plant)
