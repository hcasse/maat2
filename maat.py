#!/usr/bin/python3
#
#	MAAT top-level script
#	Copyright (C) 2022 H. Casse <hugues.casse@laposte.net>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GtNU General Public License as published by
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

"""Main module of Maat, a python-based build system."""

import argparse
import os.path
import re

import maat.common as common
import maat.io as io
import maat.rule
from maat import *


rule_re = re.compile("^([ \t]*)(.*):(.*)$")
indent_re = re.compile("^([ \t]*).*$")

# Command variables
make_name = "make.maat"
monitor = io.Monitor()
DB = maat.rule.DataBase()
first_goal = None


def fun_rule(targets, sources, fun, file, line):
	"""Build a rule from the interpretation of a script."""
	global first_goal
	rule = maat.rule.FunRule(targets, sources, fun)
	rule.file = file
	rule.line = line
	DB.add(rule)
	if first_goal == None:
		first_goal = targets[0]


# API variables
TOPDIR = common.topdir

# built-ins
join = os.path.join

def shell(cmd):
	pass


# parsing the script
class Script:
	"""Class in charge of parsing and running the script in order to
	build the rule database."""

	def __init__(self, path, env):
		self.path = path
		self.env = dict(env)

	def eval(self, mon):
		"""Process the script to build the database. In case of error,
		raise MaatError."""

		# prepare state machine
		num = 0
		NORMAL = 0
		INRULE = 1
		mode = NORMAL
		indent = None
		targets = None
		sources = None
		rnum = 0
		source = ""

		# generate rule build line
		def make(f):
			source = ""
			if num - rnum <= 1:
				source = source + indent + "\tpass\n"
			return source + "fun_rule([%s], [%s], %s, \"%s\", %s)\n" %(
				", ".join(['"%s"' % t for t in targets]),
				", ".join(['"%s"' % s for s in sources]),
				f, self.path, rnum + 1
			)

		# process the lines
		for l in open(path):
			num = num + 1
			if mode == NORMAL:
				m = rule_re.match(l)
				if m == None:
					source = source + l
				else:
					mode = INRULE
					rnum = num
					indent = m.group(1)
					targets = m.group(2).split()
					sources = m.group(3).split()
					source = source + indent + "def f():\n"
			else:
				m = indent_re.match(l)
				if len(m.group(1)) <= len(indent):
					mode = NORMAL
					source += make("f")
				source = source + l

		# final rule make if any
		if mode == INRULE:
			source += make("f")

		# process the new sources
		#print("DEBUG:", source)
		code = compile(source, self.path, "exec")
		exec(code, globals(), locals())


# parse arguments
parser = argparse.ArgumentParser(
	prog = "maat",
	description = "project maker"
)
parser.add_argument('goals', nargs='*',
	help="Goals to make.")
parser.add_argument('--print-data-base', '-p', action="store_true",
	help="Print the rule database.")
args = parser.parse_args()
path = make_name


# running the command
if not os.access(path, os.R_OK):
	monitor.print_fatal("cannot access %s" % path)
Script(path, locals()).eval(monitor)


# print the data base
if args.print_data_base:
	for rule in DB.rules:
		print(rule)

# build the goals
else:
	goals = args.goals
	if goals == []:
		goals = first_goal
