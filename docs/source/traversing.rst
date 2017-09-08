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
    Node('tests/functional')
    >>> functional_test_file.parent.parent
    Node('tests')
    >>> functional_test_file.dir
    Node('tests/functional')

Handy way to get to a directory from a file
-------------------------------------------

``.dir`` is a safe way to be in the current working directory

.. code:: python

    >>> from plant import Node
    >>>
    >>> unit_test_file = Node("tests/unit/test_base.py")
    >>> unit_test_file.dir
    Node('tests/unit')
    >>> unit_test_file.dir.dir
    Node('tests/unit')
    >>> unit_test_file.dir.dir.dir
    Node('tests/unit')
