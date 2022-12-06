#	MAAT rule classes
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

""""Classes managing the rules."""

import os.path
import maat.common as common

class Rule:
	"""Represents a rule to make a file."""

	def __init__(self, targets, sources):
		self.targets = targets
		self.sources = sources
		self.file = None
		self.line = None

	def needs_update(self):

		# get youngest target
		d = 0.
		for target in self.targets:
			try:
				fd = os.path.getmtime(target)
				if fd > d:
					d = fd
			except OSError:
				#print("DEBUG: update as %s does not exist" % target)
				return True
		#print("DEBUG: target date = %f" % d)

		# check for date in sources
		for sources in self.sources:
			try:
				fd = os.path.getmtime(source)
				if fd > d:
					#print("DEBUG: update for %s: %f", source, fd)
					return True
			except OSError:
				#print("DEBUG: update as %s does not exist" % source)
				return True

		# no update needed
		return False
		

class DataBase:
	"""Represents the database of rules, i.e. list of existing rules
	and map between files and the rule."""

	def __init__(self):
		self.rules = []
		self.map = {}

	def add(self, rule):
		self.rules.append(rule)
		for target in rule.targets:
			self.map[target] = rule

	def rule_for(self, goal):
		return self.map[goal]


class FunRule(Rule):
	"""Represents a rule which action is implemented by a function."""

	def __init__(self, targets, sources, fun):
		Rule.__init__(self, targets, sources)
		self.fun = fun

	def __repr__(self):
		return " ".join(self.targets) + ":" + " ".join(self.sources) \
			+ "\n\t" + "code %s:%d\n" % (self.file, self.line)

	def make(self, mon):
		try:
			self.fun(self)
		except common.MaatError as e:
			mon.print_error(e)
			return False
