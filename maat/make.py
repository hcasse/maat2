#	MAAT make classes
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

"""Make classes."""

import os

from maat import builtin

class Job:

	def __init__(self, rule):
		self.rule = rule

	def make(self, mon):
		self.rule.make(mon)


class Maker:
	"""Base class of makers."""

	def __init__(self, db):
		self.db = db

	def make(self, goals, mon):
		pass


class SeqMaker(Maker):
	"""Maker performing sequential make."""
	
	def __init__(self, db):
		Maker.__init__(self, db)

	def collect(self, goal):
		if goal not in self.ready:
			try:
				rule = self.db.rule_for(goal)
				if rule.needs_update():
					for source in rule.sources:
						self.collect(source)
					self.jobs.append(Job(rule))
					self.ready |= set(rule.targets)
			except KeyError:
				if not os.access(goal, os.R_OK):
					self.mon.print_fatal("no way to make %s" % goal)

	def make(self, goals, mon):
		builtin.MON = mon

		# prepare state
		self.mon = mon
		self.jobs = []
		self.ready = set()

		# collect the jobs
		for goal in goals:
			self.collect(goal)

		# build the jobs
		for job in self.jobs:
			print("DEBUG:", job.rule.targets[0])
			job.make(mon)



	
