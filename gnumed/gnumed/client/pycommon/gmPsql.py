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
import re as regex
import logging


_log = logging.getLogger('gm.bootstrapper')

_UNFORMATTABLE_ERROR_ID = 12345

#===================================================================
class Psql:

	def __init__ (self, conn):
		self.conn = conn
		self.ON_ERROR_STOP = None

	#---------------------------------------------------------------
	def fmt_msg(self, aMsg):
		try:
			tmp = "%s:%d: %s" % (self.filename, self.lineno-1, aMsg)
			tmp = tmp.replace('\r', '')
			tmp = tmp.replace('\n', '')
		except UnicodeDecodeError:
			global _UNFORMATTABLE_ERROR_ID
			tmp = "%s:%d: <cannot str(msg), printing on console with ID [#%d]>" % (self.filename, self.lineno-1, _UNFORMATTABLE_ERROR_ID)
			try:
				print('ERROR: GNUmed bootstrap #%d:' % _UNFORMATTABLE_ERROR_ID)
				print(aMsg)
			except Exception:
				pass
			_UNFORMATTABLE_ERROR_ID += 1
		return tmp

	#---------------------------------------------------------------
	def __log_pgdiag(self, exc):
		if not hasattr(exc, 'diag'):
			return

		for prop in dir(exc.diag):				# pylint: disable=no-member
			if prop.startswith('__'):
				continue
			val = getattr(exc.diag, prop)		# pylint: disable=no-member
			if val is None:
				continue
			_log.error('PG diags [%s]: %s', prop, val)

	#---------------------------------------------------------------
	def __log_notices(self):
		for notice in self.conn.notices:
			for line in notice.split('\n'):
				line = line.strip('\n').strip()
				if line:
					_log.debug(line)
		del self.conn.notices[:]

	#---------------------------------------------------------------
	def __log_session_auth(self):
		curs = self.conn.cursor()
		curs.execute('show session authorization')
		auth = curs.fetchall()[0][0]
		curs.close()
		_log.debug('session auth: %s', auth)
		return auth

	#---------------------------------------------------------------
	def run_script(self, filename) -> bool:
		"""
		filename: a file, containing semicolon-separated SQL commands
		"""
		_log.debug('processing [%s]', filename)
		if not os.access(filename, os.R_OK):
			_log.error("cannot open file [%s]", filename)
			return False

		start_auth = self.__log_session_auth()
		sql_file = open(filename, mode = 'rt', encoding = 'utf-8-sig')
		self.lineno = 0
		self.filename = filename
		currently_inside_string_literal = False
		bracketlevel = 0
		curr_cmd = ''
		curs = self.conn.cursor()
		self.ON_ERROR_STOP = True
		for line_in_sql_file in sql_file:
			self.lineno += 1
			if line_in_sql_file.strip() == '':
				continue

			# ignore "set default_transaction_read_only to ..." lines
			if regex.match(r'^\s*set\s+default_transaction_read_only\s+to\s+o.*', line_in_sql_file):
				_log.debug('ignoring "set default_transaction_read_only to ..." line')
				continue

			# process "\set ON_ERROR_STOP" lines
			if regex.match(r'^\s*\\set\s+ON_ERROR_STOP.*', line_in_sql_file):
				_log.debug('"\set ON_ERROR_STOP ..." found: end of skipping errors')
				self.ON_ERROR_STOP = True
				continue

			# process "\unset ON_ERROR_STOP" lines
			if regex.match(r'^\s*\\unset\s+ON_ERROR_STOP.*', line_in_sql_file):
				_log.debug(r'"\unset ON_ERROR_STOP" found: starting to skip errors')
				self.ON_ERROR_STOP = False
				continue

			# other '\' commands
			if not currently_inside_string_literal:
				if regex.match(r'^\\.+', line_in_sql_file):
					# most other \ commands are for controlling output formats, don't make
					# much sense in an installation script, so we gently ignore them
					_log.warning(self.fmt_msg('skipping line with psql command: %s' % line_in_sql_file))
					continue

			# non-'\' commands
			curr_char = line_in_sql_file[0]
			for next_char in line_in_sql_file[1:] + ' ':
				# detect "--"-style comments
				if curr_char == '-' and next_char == '-' and not currently_inside_string_literal:
					break

				# start/end of string detected
				if curr_char == "'":
					currently_inside_string_literal = not currently_inside_string_literal
				# detect bracketing
				if curr_char == '(' and not currently_inside_string_literal:
					bracketlevel += 1
				if curr_char == ')' and not currently_inside_string_literal:
					bracketlevel -= 1
				# have we:
				# - found end of command ?
				# - are not inside a string ?
				# - are not inside bracket pair ?
				if not ((curr_char == ';') and (currently_inside_string_literal is False) and  (bracketlevel == 0)):
					curr_cmd += curr_char
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
							if str(error).startswith('NOTICE:'):
								_log.warning(self.fmt_msg(error))
							else:
								_log.error(self.fmt_msg(error))
								self.__log_pgdiag(error)
								if self.ON_ERROR_STOP:
									self.conn.commit()
									curs.close()
									return False

						self.__log_notices()
					self.conn.commit()
					curs.close()
					curs = self.conn.cursor()
					curr_cmd = ''
				curr_char = next_char
			# end of loop over chars

		# end of loop over lines
		self.conn.commit()
		curs.close()
		end_auth = self.__log_session_auth()
		if start_auth != end_auth:
			_log.error('session auth changed before/after processing sql file')
		return True

#===================================================================
# testing code
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()
