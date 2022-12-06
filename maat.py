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
import sys
import traceback

import maat.common as common
import maat.io as io
import maat.make
import maat.rule
from maat.builtin import *
from maat import *


rule_re = re.compile("^([ \t]*)(.*):(.*)$")
indent_re = re.compile("^([ \t]*).*$")

# Command variables
SCRIPTS = {}
make_name = "make.maat"
monitor = io.Monitor()
DB = maat.rule.DataBase()
first_goal = None
scripts = {}

def maat_path(path):
	return '"%s"' % path

def maat_paths(paths):
	return " ".join([maat_path(p) for p in paths])


# variable replacement
VARS_MAP = {
	'@': '" + maat_path(maat_rule.targets[0]) + "',
	'<': '" + maat_path(maat_rule.sources[0]) + "',
	'^': '" + maat_paths(maat_rule.sources) + "'
}

VAR_RE = re.compile(r"\$([^(])|\$\(([^)]+)\)")

def expand(text):
	res = ""
	mat = VAR_RE.search(text)
	while mat:
		res = res + text[:mat.start()]
		id = mat.group(1)
		if id == None:
			id = mat.group(2)
		try:
			res = res + VARS_MAP[id]
		except KeyError:
			res = res + '" + str(%s) + "' % id
		text = text[mat.end():]
		mat = VAR_RE.search(text)
	return res + text


# API variables
TOPDIR = common.topdir

# parsing the script
class Script:
	"""Class in charge of parsing and running the script in order to
	build the rule database."""

	def __init__(self, path, env):
		self.path = path
		self.env = dict(env)
		self.linefix = []
		SCRIPTS[path] = self

	def make_rule(self, targets, sources, fun, file, line, cnum):
		global first_goal
		rule = maat.rule.FunRule(targets, sources, fun)
		rule.file = file
		rule.line = line
		DB.add(rule)
		if first_goal == None:
			first_goal = targets[0]
		self.linefix.append(cnum)

	def fix_line(self, line):
		print(line, self.linefix)
		for l in self.linefix:
			if line <= l:
				break
			line -= 1
		return line

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
			return source + "self.make_rule([%s], [%s], %s, \"%s\", %s, %s)\n" %(
				", ".join(['"%s"' % t for t in targets]),
				", ".join(['"%s"' % s for s in sources]),
				f, self.path, rnum + 1, num
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
					source = source + indent + "def f(maat_rule):\n"
			else:
				m = indent_re.match(l)
				if len(m.group(1)) <= len(indent):
					mode = NORMAL
					source += make("f")
				else:
					l = expand(l)
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


# parse the script
if not os.access(path, os.R_OK):
	monitor.print_fatal("cannot access %s" % path)
main_script = Script(path, locals())
main_script.eval(monitor)


# print the data base
if args.print_data_base:
	for rule in DB.rules:
		print(rule)

# build the goals
else:
	goals = args.goals
	if goals == []:
		goals = [first_goal]
	try:
		maat.make.SeqMaker(DB).make(goals, monitor)
	except Exception as e:
		error_re = re.compile(r'^\s*File "([^"]*)", line ([0-9]+), in')
		for f in traceback.format_tb(sys.exc_info()[2]):
			m = error_re.match(f)
			try:
				line = SCRIPTS[m.group(1)].fix_line(int(m.group(2)))
				print("%s%d%s" % (f[:m.start(2)], line, f[m.end(2):]))
			except KeyError:
				print(f)
		print("%s: %s" % (e.__class__.__name__, e))
