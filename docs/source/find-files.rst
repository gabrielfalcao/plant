.. _Find Files:

Finding files that match a certain regex
========================================

Notice that it is recursive

.. code:: python

    >>> from plant import Node
    >>>
    >>> test_files = Node("tests").find_with_regex("test_.*.py")
    >>> test_files
    [Node('tests/functional/test_fs.py'), Node('tests/unit/test_base.py'), Node('tests/unit/test_node.py')]

Finding only the first occurrence
=================================

Very handy for finding one file at a time

.. code:: python

    >>> from plant import Node
    >>>
    >>> found = Node("tests").find("test_base.py")
    >>> found
    Node('tests/unit/test_base.py')
