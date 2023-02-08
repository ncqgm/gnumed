# A Python class to replace the PSQL command-line interpreter
# NOTE: this is not a full replacement for the interpeter, merely
# enough functionality to run gnumed installation scripts
#
# Copyright (C) 2003, 2004 - 2010 GNUmed developers
# Licence: GPL v2 or later
#===================================================================
__author__ = "Ian Haywood"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# stdlib
import sys
import os
import re
import logging


_log = logging.getLogger('gm.bootstrapper')

unformattable_error_id = 12345

#===================================================================
class Psql:

	def __init__ (self, conn):
		"""
		db : the interpreter to connect to, must be a DBAPI compliant interface
		"""
		self.conn = conn
		self.vars = {'ON_ERROR_STOP': None}

	#---------------------------------------------------------------
	def match(self, pattern):
		match = re.match(pattern, self.line)
		if match is None:
			return 0

		self.groups = match.groups()
		return 1

	#---------------------------------------------------------------
	def fmt_msg(self, aMsg):
		try:
			tmp = "%s:%d: %s" % (self.filename, self.lineno-1, aMsg)
			tmp = tmp.replace('\r', '')
			tmp = tmp.replace('\n', '')
		except UnicodeDecodeError:
			global unformattable_error_id
			tmp = "%s:%d: <cannot str(msg), printing on console with ID [#%d]>" % (self.filename, self.lineno-1, unformattable_error_id)
			try:
				print('ERROR: GNUmed bootstrap #%d:' % unformattable_error_id)
				print(aMsg)
			except Exception: pass
			unformattable_error_id += 1
		return tmp

	#---------------------------------------------------------------
	def run (self, filename):
		"""
		filename: a file, containing semicolon-separated SQL commands
		"""
		_log.debug('processing [%s]', filename)
		curs = self.conn.cursor()
		curs.execute('show session authorization')
		start_auth = curs.fetchall()[0][0]
		curs.close()
		_log.debug('session auth: %s', start_auth)

		if os.access (filename, os.R_OK):
			sql_file = open(filename, mode = 'rt', encoding = 'utf-8-sig')
		else:
			_log.error("cannot open file [%s]", filename)
			return 1

		self.lineno = 0
		self.filename = filename
		in_string = False
		bracketlevel = 0
		curr_cmd = ''
		curs = self.conn.cursor()

		for self.line in sql_file:
			self.lineno += 1
			if len(self.line.strip()) == 0:
				continue

			# \set
			if self.match(r"^\\set (\S+) (\S+)"):
				_log.debug('"\set" found: %s', self.groups)
				self.vars[self.groups[0]] = self.groups[1]
				if self.groups[0] == 'ON_ERROR_STOP':
					# adjusting from string to int so that "1" -> 1 -> True
					self.vars['ON_ERROR_STOP'] = int(self.vars['ON_ERROR_STOP'])
				continue

			# \unset
			if self.match (r"^\\unset (\S+)"):
				self.vars[self.groups[0]] = None
				continue

			# other '\' commands
			if self.match (r"^\\(.*)") and not in_string:
				# most other \ commands are for controlling output formats, don't make
				# much sense in an installation script, so we gently ignore them
				_log.warning(self.fmt_msg("psql command \"\\%s\" being ignored " % self.groups[0]))
				continue

			# non-'\' commands
			this_char = self.line[0]
			# loop over characters in line
			for next_char in self.line[1:] + ' ':

				# start/end of string detected
				if this_char == "'":
					in_string = not in_string

				# detect "--"-style comments
				if this_char == '-' and next_char == '-' and not in_string:
					break

				# detect bracketing
				if this_char == '(' and not in_string:
					bracketlevel += 1
				if this_char == ')' and not in_string:
					bracketlevel -= 1

				# have we:
				# - found end of command ?
				# - are not inside a string ?
				# - are not inside bracket pair ?
				if not ((in_string is False) and (bracketlevel == 0) and (this_char == ';')):
					curr_cmd += this_char
				else:
					if curr_cmd.strip() != '':
						try:
							curs.execute(curr_cmd)
							try:
								data = curs.fetchall()
								_log.debug('cursor data: %s', data)
							except Exception:	# actually: psycopg2.ProgrammingError but no handle
								pass
						except Exception as error:
							_log.exception(curr_cmd)
							if re.match(r"^NOTICE:.*", str(error)):
								_log.warning(self.fmt_msg(error))
							else:
								_log.error(self.fmt_msg(error))
								if hasattr(error, 'diag'):
									for prop in dir(error.diag):			# pylint: disable=no-member
										if prop.startswith('__'):
											continue
										val = getattr(error.diag, prop)		# pylint: disable=no-member
										if val is None:
											continue
										_log.error('PG diags %s: %s', prop, val)
								if self.vars['ON_ERROR_STOP']:
									self.conn.commit()
									curs.close()
									return 1

					self.conn.commit()
					curs.close()
					curs = self.conn.cursor()
					curr_cmd = ''

				this_char = next_char
			# end of loop over chars

		# end of loop over lines
		self.conn.commit()
		curs.execute('show session authorization')
		end_auth = curs.fetchall()[0][0]
		curs.close()
		_log.debug('session auth after sql file processing: %s', end_auth)
		if start_auth != end_auth:
			_log.error('session auth changed before/after processing sql file')

		return 0

#===================================================================
# testing code
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#conn = PgSQL.connect(user='gm-dbo', database = 'gnumed')
	#psql = Psql(conn)
	#psql.run(sys.argv[1])
	#conn.close()
