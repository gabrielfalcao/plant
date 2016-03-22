.. _Traversing:

Every node is a file
====================

And because in unix a directory is a folder, a node might also be a
directory.

.. code:: python

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

Handy way to get to a directory from a file
-------------------------------------------

``.dir`` is a safe way to be in the current working directory

.. code:: python

    >>> from plant import Node
    >>>
    >>> unit_test_file = Node("tests/unit/test_base.py")
    >>> unit_test_file.dir
    <plant.Node (path=tests/unit)>
    >>> unit_test_file.dir.dir
    <plant.Node (path=tests/unit)>
    >>> unit_test_file.dir.dir.dir
    <plant.Node (path=tests/unit)>
