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

import os
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('plant'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages


setup(name='plant',
    version='0.1.0',
    description=('Filesystem for humans'),
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='http://github.com/gabrielfalcao/plant',
    packages=get_packages())
