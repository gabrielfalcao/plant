# -*- coding: utf-8 -*-
# <plant - filesystem for humans>
# Copyright (C) <2013>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

version = __version__ = '0.1.2'

import io
import os
import re

from fnmatch import fnmatch
from os.path import (
    abspath,
    join,
    dirname,
    exists,
    split,
    expanduser,
    basename,
    relpath
)
from os.path import isfile as isfile_base
from os.path import isdir as isdir_base


absolutify = lambda reference_path: lambda *path: join(abspath(dirname(reference_path)), *path)
LOCAL_FILE = absolutify(__file__)


def isfile(path, exists):
    if exists:
        return isfile_base(path)

    return '.' in split(path)[-1]


def isdir(path, exists):
    if exists:
        return isdir_base(path)

    return '.' not in split(path)[-1]


class DotDict(dict):
    def __getattr__(self, attr):
        try:
            return super(DotDict, self).__getattribute(attr)
        except AttributeError:
            return self[attr]

STAT_LABELS = ["mode", "ino", "dev", "nlink", "uid", "gid", "size", "atime", "mtime", "ctime"]


DOTDOTSLASH = '..{0}'.format(os.sep)


class Node(object):
    """Node is a file abstraction.

    The constructor takes a path as a parameter and grabs filesystem
    information about it.

    Its attributes `is_file` and `isdir` are booleans and are useful
    for quickly identifying its 'type', which among Plant's engine
    codebase is either 'blob', for a file and 'dir' for a directory.

    It also has `self.metadata`, which is just a handy `DotDict`
    containing the results of calling `os.stat` (mode, ino, dev,
    nlink, uid, giu, size, atime, mtime, ctime)
    """
    def __init__(self, path):
        self.path = abspath(expanduser(path)).rstrip('/')
        self.path_regex = '^{0}'.format(re.escape(self.path))
        try:
            stats = os.stat(self.path)
            self.exists = True
        except OSError:
            stats = [0] * len(STAT_LABELS)
            self.exists = False

        self.metadata = DotDict(zip(STAT_LABELS, stats))
        self.is_file = isfile(self.path, exists=self.exists)
        self.is_dir = isdir(self.path, exists=self.exists)

    @classmethod
    def new(cls, *args, **kw):
        """creates a new instance of :py:class:`Node` mostly used internally
        by its methods.

        :param ``*args``:
        :param ``**kw``:
        :returns: a new instance of :py:class:`Node`
        """
        return cls(*args, **kw)

    @property
    def basename(self):
        """extracts the basename the node path

        ::

            >>> from plant import Node
            >>>
            >>> Node('/srv/application/conf.py').basename
            'conf.py'


        :returns: :py:class:`bytes`
        """
        return basename(self.path)

    def list(self):
        """returns a list of files children of the current directory
        if the node points to a file, it's siblings will be listed

        ::

            >>> from plant import Node
            >>>
            >>> Node('/srv/application/conf.py').list()
            [
                Node('/srv/application/conf.py'),
                Node('/srv/application/README.rst')
            ]

        :returns: a  :py:class:`list` of :py:class:`Node`
        """
        return list(map(self.new, os.listdir(self.dir.path)))

    @property
    def dir(self):
        """returns a :py:class:`Node` pointing to the current directory.

        this call is idempotent in the sense that chaining up multiple
        class results in the same node.

        ::

            >>> from plant import Node
            >>>
            >>> Node('/srv/application/conf.py').dir
            Node('/srv/application')
            >>>
            >>> Node('/srv/application/conf.py').dir.dir
            Node('/srv/application')
            >>>
            >>> Node('/srv/application/conf.py').dir.dir.dir
            Node('/srv/application')
            >>>
            >>> # and so on

        :returns: :py:class:`Node`

        """
        if not self.is_dir:
            return self.parent
        else:
            return self

    @property
    def directory(self):
        """shortcut for :py:attr:`Node.dir`

        ::

            >>> from plant import Node
            >>>
            >>> Node('/srv/application/conf.py').directory
            Node('/srv/application')
            >>>
            >>> Node('/srv/application/conf.py').directory.directory
            Node('/srv/application')
            >>>
            >>> Node('/srv/application/conf.py').directory.directory.directory
            Node('/srv/application')
            >>>
            >>> # and so on

        :returns: :py:class:`Node`
        """
        return self.dir

    @property
    def parent(self):
        """returns a :py:class:`Node` pointing to the parent directory.

        it stops at the root node.

        ::

            >>> from plant import Node
            >>>
            >>> Node('/srv/application').parent
            Node('/srv')
            >>>
            >>> Node('/srv/application').parent.parent
            Node('/')
            >>>
            >>> # it stops at the root node
            >>> Node('/srv/application').parent.parent.parent
            Node('/')


        :returns: :py:class:`Node`
        """
        return self.new(dirname(self.path))

    def could_be_updated_by(self, other):
        """check to see if the ``mtime`` of another :py:class:`Node` is greater than the current one.

        :param other: the other :py:class:`Node`
        :returns: bool - true if the other node is "newer"
        """
        return self.metadata.mtime < other.metadata.mtime

    def relative(self, path):
        """returns the relative from the current :py:class:`Node` to the given string

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media/mp3/').relative('/opt/media/mp4/my-video.mp4')
           '../mp4/my-video.mp4'

        :param path: a path string
        :returns: :py:class:`bytes`
        """
        return re.sub(self.path_regex, '', path).lstrip(os.sep)

    def trip_at(self, path, lazy=False):
        """Iterates recursively on a subpath of the current :py:class:`Node`

        It basically performs a py:func:`os.walk` at the given path and yields the absolute path
        to each file

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media').trip_at('mp3', lazy=False)
           [
               '/opt/media/mp3/music1.mp3',
               '/opt/media/mp3/music2.mp3',
            ]

        :param path: a path string
        :param lazy: bool - if True returns an iterator, defaults to a flat :py:class:`list`
        :returns: an iterator or a list of :py:class:`bytes`
        """
        def iterator():
            for root, folders, filenames in os.walk(self.join(path)):
                for filename in filenames:
                    yield join(root, filename)

        return lazy and iterator() or list(iterator())

    def walk(self, lazy=False):
        """Same as :py:meth:`Node.trip_at` but iterates recursively within the current :py:class:`Node` instead.

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media').walk(lazy=False)
           [
               '/opt/media/mp3/music1.mp3',
               '/opt/media/mp3/music2.mp3',
               '/opt/media/mp4/my-video.mp4',
            ]

        :param path: a path string
        :param lazy: bool - if True returns an iterator, defaults to a flat :py:class:`list`
        :returns: an iterator or a list of :py:class:`bytes`
        """
        return self.trip_at(self.path, lazy=lazy)

    def glob(self, pattern, lazy=False):
        """
        searches for globs recursively in all the children node of the
        current node returning a respective [python`Node`] instance
        for that given.

        Under the hood it applies the given ``pattern`` into :py:func:`fnmatch.fnmatch`

        ::

           >>> from plant import Node
           >>>
           >>> mp3_node = Node('/opt/media/mp3')
           >>> mp3_node.glob('*.mp3')
           [
               Node('/opt/media/mp3/music1.mp3'),
               Node('/opt/media/mp3/music2.mp3'),
            ]

        :param pattern: a valid :py:mod:`fnmatch` pattern string
        :param lazy: bool - if True returns an iterator, defaults to a flat :py:class:`list`
        :returns: an iterator or a list of :py:class:`Node`
        """
        def iterator():
            for filename in self.walk(lazy=lazy):
                if fnmatch(filename, pattern):
                    yield self.new(filename)

        return lazy and iterator() or list(iterator())

    def find_with_regex(self, pattern, flags=0, lazy=False):
        """
        searches recursively for children that match the given regex
        returning a respective [python`Node`] instance for that given.

        It works like :py:meth:`Node.glob` but applies a regexp match rather instead.

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media').find_with_regex('[.](mp3|mp4)$')
           [
               Node('/opt/media/mp3/music1.mp3'),
               Node('/opt/media/mp3/music2.mp3'),
               Node('/opt/media/mp4/my-video.mp4'),
            ]

        :param pattern: a valid :py:mod:`fnmatch` pattern string
        :param lazy: bool - if True returns an iterator, defaults to a flat :py:class:`list`
        :returns: an iterator or a list of :py:class:`Node`
        """

        def iterator():
            for filename in self.walk(lazy=lazy):
                if re.search(pattern, filename, flags):
                    yield self.new(filename)

        return lazy and iterator() or list(iterator())

    def __eq__(self, other):
        """Compares two :py:class:`Node` objects
           Under the hood it compares the path and the metadata (permissions, ownership)

           >>> from plant import Node
           >>>
           >>> node1 = Node('/opt/media')
           >>> node2 = Node('/opt/media')
           >>> node3 = Node('/opt/media/mp3')
           >>> node1 == node2
           True
           >>> node3 == node1
           False
        """
        return self.path == other.path and self.metadata == other.metadata

    def find(self, relative_path):
        """Calls :py:meth:`Node.find_with_regex` with ``lazy=True`` but only
        returns the first occurrence.

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media').find('[.](mp3|mp4)$')
           Node('/opt/media/mp3/music1.mp3')

        :param relative_path: :py:class:`bytes`
        :returns: a :py:class:`Node`
        """
        for found in self.find_with_regex(relative_path, lazy=True):
            return found

        return None

    def depth_of(self, path):
        """Calculates the level of depth of the given path inside of the
        instance's path.

        Only really works with paths that are relative to the class.

        ::

           >>> from plant import Node
           >>>
           >>> level = Node('/foo/bar').depth_of('/foo/bar/another/dir/file.py')
           >>> level
           2

        :param path: :py:class:`bytes`
        :returns: a :py:class:`bool`
        """
        new_path = self.relative(path)
        final_path = self.join(new_path)
        if isfile(final_path, exists(final_path)):
            new_path = dirname(new_path)

        new_path = new_path.rstrip('/')
        new_path = "{0}/".format(new_path)
        return new_path.count(os.sep)

    def path_to_related(self, path):
        """Returns the path to a related file. (is under a subtree the
        same tree as the node).

        It's useful to know how to go back to the root of this node
        instance.

        ::

            >>> from plant import Node
            >>>
            >>> way_back = Node('/foo/bar').path_to_related('/foo/bar/another/dir/file.py')
            >>> way_back
            '../../'

            >>> way_back = Node('/foo/bar/docs/static/file.css').path_to_related('/foo/bar/docs/intro/index.md')
            >>> way_back
            '../static/file.css'

        :param path: :py:class:`bytes`
        :returns: a :py:class:`bytes`
        """
        # self.path = "...functional/fixtures/img/logo.png"
        # path = "...functional/fixtures/docs/index.md"
        current = self.dir

        while not path.startswith(current.dir.path):
            current = current.dir.parent.dir

        remaining = current.relative(self.path)

        level = current.relative(path).count(os.sep)

        way_back = os.sep.join(['..'] * level) or '.'
        result = "{0}/{1}".format(way_back, remaining)

        return result

    def goto(self, path):
        """Returns a :py:class:`Node` pointing to the given directory

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media/mp3/').goto('../mp4/my-video.mp4')
           Node('/opt/media/mp4/my-video.mp4')

        :param path: :py:class:`bytes`
        :returns: a :py:class:`Node`
        """
        return self.new(self.join(path))

    def cd(self, path):
        """Shortcut for :py:meth:`Node.goto`, also works for files, though has
        a better semantic outlook when handling directories.

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media/mp3').cd('../mp4')
           Node('/opt/media/mp4')

        :param path: :py:class:`bytes`
        :returns: a :py:class:`Node`
        """

        return self.new(self.join(path))

    def contains(self, path):
        """Checks if the given path exists as an immediate relative of the current node's path

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media/mp3').contains('unknown-track.mp3')
           False
           >>>
           >>> Node('/opt/media/mp4').contains('../mp3/music1.mp3')
           True

        :param path: :py:class:`bytes`
        :returns: :py:class:`bool`
        """

        return exists(self.join(path))

    def join(self, *path):
        """Joins the given path with that of the current node's

        Does not check if the target file exists, it simply concatenates strings using the native platform's path separator.

        ::

           >>> from plant import Node
           >>>
           >>> Node('/opt/media/mp3').join('unknown-track.mp3')
           '/opt/media/mp3/unknown-track.mp3'

           >>> Node('/opt/media/mp4').join('..' , 'mp3', 'music1.mp3')
           '/opt/media/mp3/music1.mp3'

        :param path: :py:class:`bytes`
        :returns: :py:class:`bytes`
        """
        return abspath(join(self.path, *path))

    def open(self, path, *args, **kw):
        """performs an :py:func:`io.open` on the given relative path to the current node.

        ::

           >>> from plant import Node
           >>>
           >>> documents = Node('/opt/documents')

           >>> with documents.open('hello-world.txt', 'wb', 'utf-8') as f:
           ...     f.write('HELLO WORLD')

           >>> documents.open('hello-world.txt').read()
           'HELLO WORLD'

        :param path: :py:class:`bytes`
        :param ``*args``: passed onto :py:func:`io.open`
        :param ``*kw``: passed onto :py:func:`io.open`
        :returns: :py:class:`io.FileIO`
        """
        return io.open(self.join(path), *args, **kw)

    def __repr__(self):
        """string representation of a :py:class:`Node`

        ::

           >>> from plant import Node
           >>>
           >>> repr(Node('/opt/documents'))
           'Node("/opt/documents")'
        """
        return 'Node({0})'.format(repr(relpath(self.path)))
