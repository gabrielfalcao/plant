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

version = __version__ = '0.1.0'

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

    @property
    def basename(self):
        return basename(self.path)

    def list(self):
        return map(self.__class__, os.listdir(self.dir.path))

    @property
    def dir(self):
        if not self.is_dir:
            return self.parent
        else:
            return self

    @property
    def parent(self):
        return self.__class__(dirname(self.path))

    def could_be_updated_by(self, other):
        return self.metadata.mtime < other.metadata.mtime

    def relative(self, path):
        """##### `Node#relative(path)`

        returns a given path subtracted by the node.path [python`unicode`]

        ```python
        rel = Node('/Users/gabrielfalcao/').relative('/Users/gabrielfalcao/profile-picture.png')
        assert rel == 'profile-picture.png'
        ```
        """
        return re.sub(self.path_regex, '', path).lstrip(os.sep)

    def trip_at(self, path, lazy=False):
        """ ##### `Node#trip_at(path)`

        does a os.walk at the given path and yields the absolute path
        to each file

        ```python
        for filename in node.trip_at('/etc/smb'):
            print filename
        ```
        """
        def iterator():
            for root, folders, filenames in os.walk(self.join(path)):
                for filename in filenames:
                    yield join(root, filename)

        return lazy and iterator() or list(iterator())

    def walk(self, lazy=False):
        return self.trip_at(self.path, lazy=lazy)

    def glob(self, pattern, lazy=False):
        """ ##### `Node#glob(pattern)`

        searches for globs recursively in all the children node of the
        current node returning a respective [python`Node`] instance
        for that given.

        ```python
        for node in Node('/Users/gabrifalcao').glob('*.png'):
            print node.path  # will print the absolute
                             # path of the found file
        ```
        """
        def iterator():
            for filename in self.walk(lazy=lazy):
                if fnmatch(filename, pattern):
                    yield self.__class__(filename)

        return lazy and iterator() or list(iterator())

    def find_with_regex(self, pattern, flags=0, lazy=False):
        """ ##### `Node#find_with_regex(pattern)`

        searches recursively for children that match the given regex
        returning a respective [python`Node`] instance for that given.

        ```python
        for node in Node('/Users/gabrifalcao').glob('*.png'):
            print node.path  # will print the absolute
                             # path of the found file
        ```
        """

        def iterator():
            for filename in self.walk(lazy=lazy):
                if re.search(pattern, filename, flags):
                    yield self.__class__(filename)

        return lazy and iterator() or list(iterator())

    def __eq__(self, other):
        return self.path == other.path and self.metadata == other.metadata

    def find(self, relative_path):
        """ ##### `Node#find(relative_path)`

        Returns the first file that matches the given relative path.
        Returns None if nothing is returned.

        If nothing is found, returns None
        ```python

        logo = Node('~/projects/personal/plant').find('logo.png')
        assert logo.path == os.path.expanduser('~/projects/personal/plant/logo.png')
        ```
        """
        found = list(self.find_with_regex(relative_path, lazy=True))
        if found:
            return found[0]

        return None

    def depth_of(self, path):
        """Returns the level of depth of the given path inside of the
        instance's path.

        Only really works with paths that are relative to the class.

        ```python
        level = Node('/foo/bar').depth_of('/foo/bar/another/dir/file.py')
        assert level == 2
        ```
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

        ```python
        way_back = Node('/foo/bar').path_to_related('/foo/bar/another/dir/file.py')
        assert way_back == '../../'

        way_back = Node('/foo/bar/docs/static/file.css').path_to_related('/foo/bar/docs/intro/index.md')
        assert way_back == '../static/file.css'
        ```
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

    def cd(self, path):
        return self.__class__(self.join(path))

    def contains(self, path):
        return exists(self.join(path))

    def join(self, path):
        return abspath(join(self.path, path))

    def open(self, path, *args, **kw):
        return io.open(self.join(path), *args, **kw)

    def __repr__(self):
        return '<plant.Node (path={0})>'.format(relpath(self.path))
