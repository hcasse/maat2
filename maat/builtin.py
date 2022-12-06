#	MAAT built-in functions
#	Copyright (C) 2022 H. Casse <hug.casse@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Built-in functions."""

import re

import os.path

# state
MON = None


# aliases
join = os.path.join


def shell(cmd):
	"""Implements the shell(...) function"""
	MON.print_info(cmd)


def echo(*args):
	"""Command displaying something."""
	MON.print(" ".join([str(a) for a in args]))
