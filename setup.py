# #!/usr/bin/env python
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

import ast
import codecs
import os

from setuptools import setup, find_packages


def local_file(*f):
    path = os.path.join(os.path.dirname(__file__), *f)
    return codecs.open(path, 'r', encoding='utf-8').read().encode('utf-8')


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('plural', 'version.py')))
    return finder.version


# install_requires = list(filter(bool, map(bytes.strip, local_file('requirements.txt').splitlines())))


setup(name='plant',
      version=read_version(),
      description=('Filesystem for humans'),
      author='Gabriel Falcao',
      author_email='gabriel@nacaolivre.org',
      url='http://github.com/gabrielfalcao/plant',
      packages=find_packages(local_file('tests')))
