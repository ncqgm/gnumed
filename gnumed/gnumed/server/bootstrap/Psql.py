# A Python class to replace the PSQL command-line interpreter
# NOTE: his is not a full replacement for the interpeter, merely
# enough functionality to run gnukmed installation scripts
# Copyright (C) 2003 GNUMed developers
# Licence: GPL

import sys, os, string, re
sys.path.append ('../../client/pycommon')
import gmLog
_log = gmLog.gmDefLog

#===================================================================
def shellrun (cmd):
	"""
	runs the shell command and returns a string
	"""
	stdin, stdout = os.popen4 (cmd.group (1))
	r = stdout.read ()
	stdout.close ()
	stdin.close ()
	return r

def shell (str):
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

	def match (self, str):
		match = re.match (str, self.line)
		if match is None:
			ret = 0
		else:
			ret = 1
			self.groups = match.groups ()
		return ret

	def fmt_msg(self, aMsg):
		tmp = string.replace("%s:%d: %s" % (self.filename, self.lineno, aMsg), '\r', '')
		return string.replace(tmp, '\n', '')

	def log (self, level, str):
	   gmLog.gmDefLog.Log (level, "%s: line %d: %s" % (self.filename, self.lineno, str))
		
	def run (self, filename):
		"""
		filename: a file, containg semicolon-separated SQL commands
		"""
		if os.access (filename, os.R_OK):
			self.file = open(filename)
		else:
			_log.Log (gmLog.lErr, "cannot open file [%s]" % filename)
			return 1
		self.cmd = ''
		self.lineno = 0
		self.filename = filename
		instring = 0
		bracketlevel = 0
		for self.line in self.file.readlines():
			if len (self.line) > 0:
				# process \ commands
				if self.match (r"^\\echo (.*)"):
					_log.Log (gmLog.lInfo, self.fmt_msg(shell (self.groups[0])))
				elif self.match (r"^\\qecho (.*)"):
					_log.Log (gmLog.lInfo, self.fmt_msg(shell (self.groups[0])))
				elif self.match (r"^\\q"):
					_log.Log (gmLog.lWarn, self.fmt_msg("script terminated by \\q"))
					return 0
				elif self.match (r"^\\set (\S+) (\S+)"):
					self.vars[self.groups[0]] = shell (self.groups[1])
					if self.groups[0] == 'ON_ERROR_STOP':
						self.vars['ON_ERROR_STOP'] = int (self.vars['ON_ERROR_STOP'])
				elif self.match (r"^\\unset (\S+)"):
					self.vars[self.groups[0]] = None
				elif self.match (r"^\\connect.*"):
					_log.Log (gmLog.lErr, self.fmt_msg("\\connect not yet supported in scripts"))
				elif self.match (r"^\\lo_import.*"):
					_log.Log (gmLog.lErr, self.fmt_msg("\\lo_import not yet supported"))
					# no sense to continue here
					return 1
				elif self.match (r"^\\copy .* to '(\S+)' .*"):
					_log.Log (gmLog.lErr, self.fmt_msg("\\copy to not implemented"))
					return 1
				elif self.match (r"^\\copy .* from '(\S+)' .*"):
					copyfile = self.groups[0]
					try:
						copyfd = file (os.path.join (os.path.dirname (self.filename), copyfile))
					except error:
						_log.Log (gmLog.lErr, self.fmt_msg(error))
						return 1
					self.line = self.line[1:] # lop off leading slash
					self.line.strip ()
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
						gmLog.gmDefLog.Log (gmLog.lErr, "%s: %d: %s" % (copyfile, copyline, error))
						if self.vars['ON_ERROR_STOP']:
							return 1
				elif self.match (r"^\\i (\S+)"):
					# create another interpreter instance in same connection
					Psql(self.conn).run (os.path.join (os.path.dirname (self.filename), self.groups[0]))
				elif self.match (r"^\\encoding.*"):
					_log.Log (gmLog.lErr, self.fmt_msg("\\encoding not yet supported"))
				elif self.match (r"^\\(.*)") and not instring:
					# most other \ commands are for controlling output formats, don't make
					# much sense in an installation script, so we gently ignore them
					_log.Log (gmLog.lWarn, self.fmt_msg("psql command \"\\%s\" being ignored " % self.groups[0]))
				else:
					i = self.line[0]
					for next in self.line[1:] + ' ':
						if i == "'":
							if instring:
								instring = 0
							else:
								instring = 1
						if i == '-' and next == '-'and not instring:
							break
						if i == '(' and not instring:
							bracketlevel += 1
						if i == ')' and not instring:
							bracketlevel -= 1
						if not instring and bracketlevel == 0 and i == ";":
							try:
								curs = self.conn.cursor ()
								curs.execute (self.cmd)
								self.conn.commit ()
								curs.close ()
							except StandardError, error:
								_log.Log (gmLog.lData, self.cmd)
								if re.match (r"^NOTICE:.*", str(error)):
									_log.Log (gmLog.lWarn, self.fmt_msg(error))
								else:
									if self.vars['ON_ERROR_STOP']:
										_log.Log (gmLog.lErr, self.fmt_msg(error))
										return 1
									else:
										_log.Log (gmLog.lData, self.fmt_msg(error))
							self.cmd = ''
						else:
							self.cmd += i
						i = next
			self.lineno += 1
		return 0


def shell (str):
	return re.sub ("`(.*)`", shellrun, str)

#===================================================================
# testing code
if __name__ == '__main__':
	from pyPgSQL import PgSQL
	conn = PgSQL.connect (user='gm-dbowner', database = 'gnumed')
	psql = Psql (conn)
	psql.run (sys.argv[1])
	conn.close ()
