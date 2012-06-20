# A Python class to replace the PSQL command-line interpreter
# NOTE: this is not a full replacement for the interpeter, merely
# enough functionality to run gnumed installation scripts
#
# Copyright (C) 2003, 2004 - 2010 GNUmed developers
# Licence: GPL v2 or later
#===================================================================
__author__ = "Ian Haywood"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# stdlib
import sys, os, string, re, urllib2, logging


_log = logging.getLogger('gm.bootstrapper')

unformattable_error_id = 12345
#===================================================================
def shellrun (cmd):
	"""
	runs the shell command and returns a string
	"""
	stdin, stdout = os.popen4 (cmd.group (1))
	r = stdout.read ()
	stdout.close()
	stdin.close()
	return r
#-------------------------------------------------------------------
def shell(str):
	"""
	performs backtick shell extension in a string
	"""
	return re.sub (r"`(.*)`", shellrun, str)
#===================================================================
class Psql:

	def __init__ (self, conn):
		"""
		db : the interpreter to connect to, must be a DBAPI compliant interface
		"""
		self.conn = conn
		self.vars = {'ON_ERROR_STOP':None}
	#---------------------------------------------------------------
	def match (self, str):
		match = re.match (str, self.line)
		if match is None:
			ret = 0
		else:
			ret = 1
			self.groups = match.groups ()
		return ret
	#---------------------------------------------------------------
	def fmt_msg(self, aMsg):
		try:
			tmp = u"%s:%d: %s" % (self.filename, self.lineno-1, aMsg)
			tmp = tmp.replace(u'\r', u'')
			tmp = tmp.replace(u'\n', u'')
		except UnicodeDecodeError:
			global unformattable_error_id
			tmp = u"%s:%d: <cannot unicode(msg), printing on console with ID [#%d]>" % (self.filename, self.lineno-1, unformattable_error_id)
			try:
				print 'ERROR: GNUmed bootstrap #%d:' % unformattable_error_id
				print aMsg
			except: pass
			unformattable_error_id += 1
		return tmp
	#---------------------------------------------------------------
	def run (self, filename):
		"""
		filename: a file, containg semicolon-separated SQL commands
		"""
		if re.match ("http://.*", filename) or re.match ("ftp://.*", filename) or re.match ("gopher://.*", filename):
			try:
				self.file = urllib2.urlopen (filename)
			except URLError:
				_log.error(u"cannot access %s" % filename)
				return 1
		else:
			if os.access (filename, os.R_OK):
				self.file = open(filename)
			else:
				_log.error(u"cannot open file [%s]" % filename)
				return 1

		self.lineno = 0
		self.filename = filename
		in_string = False
		bracketlevel = 0
		curr_cmd = ''
		curs = self.conn.cursor ()
#		transaction_started = False
		for self.line in self.file.readlines():
			self.lineno += 1
			if len(self.line.strip()) == 0:
				continue

			# \echo
			if self.match (r"^\\echo (.*)"):
				_log.info(self.fmt_msg(shell(self.groups[0])))
				continue
			# \qecho
			if self.match (r"^\\qecho (.*)"):
				_log.info(self.fmt_msg(shell (self.groups[0])))
				continue
			# \q
			if self.match (r"^\\q"):
				_log.warning(self.fmt_msg(u"script terminated by \\q"))
				return 0
			# \set
			if self.match (r"^\\set (\S+) (\S+)"):
				self.vars[self.groups[0]] = shell (self.groups[1])
				if self.groups[0] == 'ON_ERROR_STOP':
					self.vars['ON_ERROR_STOP'] = int (self.vars['ON_ERROR_STOP'])
				continue
			# \unset
			if self.match (r"^\\unset (\S+)"):
				self.vars[self.groups[0]] = None
				continue
			# \connect
			if self.match (r"^\\connect.*"):
				_log.error(self.fmt_msg(u"\\connect not yet supported in scripts"))
				continue
			# \lo_import
			if self.match (r"^\\lo_import.*"):
				_log.error(self.fmt_msg(u"\\lo_import not yet supported"))
				# no sense to continue here
				return 1
			# \copy ... to ...
			if self.match (r"^\\copy .* to '(\S+)' .*"):
				_log.error(self.fmt_msg(u"\\copy to not implemented"))
				return 1
			# \copy ... from ...
			if self.match (r"^\\copy .* from '(\S+)' .*"):
				copyfile = self.groups[0]
				try:
					copyfd = file (os.path.join (os.path.dirname (self.filename), copyfile))
				except error:
					_log.error(self.fmt_msg(error))
					return 1
				self.line = self.line[1:].strip() # lop off leading slash
				self.line.replace ("'%s'" % copyfile, 'stdin')
				# now we have a command that the backend understands
				copyline = 0
				try:
					curs = self.conn.cursor ()
					# send the COPY command
					curs.execute (self.line)
					# send the data
					for i in copyfd.readlines ():
						curs.execute (i)
						copyline += 1
					self.conn.commit ()
					curs.close ()
				except StandardError, error:
					_log.error(u"%s: %d: %s" % (copyfile, copyline, error))
					if self.vars['ON_ERROR_STOP']:
						return 1
				continue

			# \i
			if self.match (r"^\\i (\S+)"):
				# create another interpreter instance in same connection
				Psql(self.conn).run (os.path.join (os.path.dirname (self.filename), self.groups[0]))
				continue

			# \encoding
			if self.match (r"^\\encoding.*"):
				_log.error(self.fmt_msg(u"\\encoding not yet supported"))
				continue

			# other '\' commands
			if self.match (r"^\\(.*)") and not in_string:
				# most other \ commands are for controlling output formats, don't make
				# much sense in an installation script, so we gently ignore them
				_log.warning(self.fmt_msg(u"psql command \"\\%s\" being ignored " % self.groups[0]))
				continue

			# non-'\' commands
			this_char = self.line[0]
			# loop over characters in line
			for next_char in self.line[1:] + ' ':

				# start/end of string detected
				if this_char == "'":
					in_string = not in_string

				# detect -- style comments
				if this_char == '-' and next_char == '-' and not in_string:
					break

				# detect bracketing
				if this_char == '(' and not in_string:
					bracketlevel += 1
				if this_char == ')' and not in_string:
					bracketlevel -= 1

				# found end of command, not inside string, not inside bracket ?
				if not (not in_string and (bracketlevel == 0) and (this_char == ';')):
					curr_cmd += this_char
				else:
					try:
#						if curr_cmd.strip ().upper () == 'COMMIT':
#							if transaction_started:
#								self.conn.commit ()
#								curs.close ()
#								curs = self.conn.cursor ()
#								_log.debug(self.fmt_msg ("transaction committed"))
#							else:
#								_log.warning(self.fmt_msg ("COMMIT without BEGIN: no actual transaction happened!"))
#							transaction_started = False

#						elif curr_cmd.strip ().upper () == 'BEGIN':
#							if transaction_started:
#								_log.warning(self.fmt_msg ("BEGIN inside transaction"))
#							else:
#								transaction_started = True
#								_log.debug(self.fmt_msg ("starting transaction"))

#						else:
						if curr_cmd.strip() != '':
							if curr_cmd.find('vacuum'):
								self.conn.commit();
								curs.close()
								old_iso_level = self.conn.isolation_level
								self.conn.set_isolation_level(0)
								curs = self.conn.cursor()
								curs.execute (curr_cmd)
								self.conn.set_isolation_level(old_iso_level)
							else:
								curs.execute (curr_cmd)
#								if not transaction_started:
					except StandardError, error:
						_log.debug(curr_cmd)
						if re.match (r"^NOTICE:.*", str(error)):
							_log.warning(self.fmt_msg(error))
						else:
							if self.vars['ON_ERROR_STOP']:
								_log.error(self.fmt_msg(error))
								return 1
							else:
								_log.debug(self.fmt_msg(error))

					self.conn.commit()
					curs.close()
					curs = self.conn.cursor()
					curr_cmd = ''

				this_char = next_char

			# end of loop over chars

		# end of loop over lines
		self.conn.commit()
		curs.close()
		return 0
#===================================================================
# testing code
if __name__ == '__main__':
	from pyPgSQL import PgSQL
	conn = PgSQL.connect (user='gm-dbo', database = 'gnumed')
	psql = Psql (conn)
	psql.run (sys.argv[1])
	conn.close ()
#===================================================================
