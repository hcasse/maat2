#	MAAT top-level script
#	Copyright (C) 2016 H. Casse <hugues.casse@laposte.net>
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

"""Input/output management module for Maat tool."""
import sys

# ANSI coloration
NORMAL = "\033[0m"
"""Switch back console display to normal mode."""
BOLD = "\033[1m"
"""Switch console display to bold."""
FAINT = "\033[2m"
"""Switch console display to faint."""
ITALIC = "\033[3m"
"""Switch console display to italic."""
UNDERLINE = "\033[4m"
"""Switch console display to underline."""
BLACK = "\033[30m"
"""Switch console display to foreground black."""
RED = "\033[31m"
"""Switch console display to foreground red."""
GREEN = "\033[32m"
"""Switch console display to foreground green."""
YELLOW = "\033[33m"
"""Switch console display to foreground yellow."""
BLUE = "\033[34m"
"""Switch console display to foreground blue."""
MAGENTA = "\033[35m"
"""Switch console display to foreground magenta."""
CYAN = "\033[36m"
"""Switch console display to foreground cyan."""
WHITE = "\033[37m"
"""Switch console display to foreground white."""
BACK_BLACK = "\033[40m"
"""Switch console display to background black."""
BACK_RED = "\033[41m"
"""Switch console display to background red."""
BACK_GREEN = "\033[42m"
"""Switch console display to background green."""
BACK_YELLOW = "\033[43m"
"""Switch console display to background yellow."""
BACK_BLUE = "\033[44m"
"""Switch console display to background blue."""
BACK_MAGENTA = "\033[45m"
"""Switch console display to background magenta."""
BACK_CYAN = "\033[46m"
"""Switch console display to background cyan."""
BACK_WHITE = "\033[47m"
"""Switch console display to background white."""


# execution context
#class NullStream:
#	"""Stream that prints nothings."""
#	
#	def write(self, line):
#		pass


#null_stream = NullStream()

class Monitor:
	"""A context is used to configure the execution of an action."""
	out = sys.stdout
	err = sys.stderr
	quiet = False
	verbose = False
	flushed = False
	action = None
	
	def handle_action(self):
		"""Manage a pending action display."""
		if self.action and not self.flushed:
			sys.stderr.write("\n")
			self.flushed = True
	
	def print_command(self, cmd):
		"""Print a command before running it."""
		if not self.quiet and self.command_ena:
			self.handle_action()
			sys.stderr.write(CYAN + "> " + str(cmd) + NORMAL + "\n")
			sys.stderr.flush()
	
	def print_info(self, info):
		"""Print information line about built target."""
		if not self.quiet:
			self.handle_action()
			sys.stderr.write(BOLD + BLUE + str(info) + NORMAL + "\n")
			sys.stderr.flush()

	def print_error(self, msg):
		"""Print an error message."""
		if not self.quiet:
			self.handle_action()
			sys.stderr.write(BOLD + RED + "ERROR: " + str(msg) + NORMAL + "\n")
			sys.stderr.flush()
	
	def print_fatal(self, msg):
		"""Print an error message."""
		if not self.quiet:
			sys.stderr.write(BOLD + RED + "ERROR: " + str(msg) + NORMAL + "\n")
			sys.exit(1)
	
	def print_warning(self, msg):
		"""Print a warning message."""
		if not self.quiet:
			self.handle_action()
			sys.stderr.write(BOLD + YELLOW + "WARNING: " + str(msg) + NORMAL + "\n")
			sys.stderr.flush()

	def print_success(self, msg):
		"""Print a success message."""
		if not self.quiet:
			self.handle_action()
			sys.stderr.write(BOLD + GREEN + "[100%] " + msg + str(NORMAL) + "\n")
			sys.stderr.flush()

	def print_action(self, msg):
		"""Print a beginning action."""
		if not self.quiet:
			sys.stderr.write("%s ... " % msg)
			sys.stderr.flush()
			self.action = msg
			self.flushed = False
	
	def print_final(self, msg):
		if not self.quiet:
			if self.flushed:
				sys.stderr.write("%s ... " % self.action)				
			sys.stderr.write(msg)
			sys.stderr.write("\n");
			sys.stderr.flush()
			self.action = None
			self.flushed = False
	
	def print_success(self, msg = ""):
		"""End an action with success."""
		if msg:
			msg = "(%s) " % msg
		self.print_action_final(msg + GREEN + BOLD + "[OK]" + NORMAL)

	def print_failure(self, msg = ""):
		"""End an action with failure."""
		if msg:
			msg = "(%s) " % msg
		self.print_action_final(msg + RED + BOLD + "[FAILED]" + NORMAL)

	def print(self, msg):
		if sys.stderr == sys.stdout:
			self.handle_action()
		sys.stdout.write(msg + "\n")
		sys.stdout.flush()
		

DEF = Monitor()		# better to remove it at some point
