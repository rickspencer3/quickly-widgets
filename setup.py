#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
#This program is free software: you can redistribute it and/or modify it 
#under the terms of the GNU General Public License version 3, as published 
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along 
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, 'To build quidgets you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)

assert DistUtilsExtra.auto.__version__ >= '2.10', 'needs DistUtilsExtra.auto >= 2.10'
import os


##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='quickly-widgets',
    version='10.2',
    license='GPL-3',
    author='Rick Spencer',
    author_email='rick.spencer@canonical.com',
    description='Library for easing some PyGtk coding tasks',
    long_description='Library for easing some PyGtk coding tasks. Note that this is experimental, the API will change, there are bugs.',
    url='http://launchpad.net/quidgets',
    )

