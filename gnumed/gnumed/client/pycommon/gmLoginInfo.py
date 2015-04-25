############################################################################
# gmLoginInfo - a class to encapsulate Postgres login information
############################################################################
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging

_log = logging.getLogger('gm.db')
#====================================================================
class LoginInfo:
	"""a class to encapsulate Postgres login information to default database"""

	# private variables
#	user = ''
#	password = ''
#	host = ''
#	port = 5432
#	database = ''
	#------------------------------------------
	def __init__(self, user=None, password=None, host=None, port=5432, database=None):
		self.user = user
		self.password = password
		self.host = host
		self.port = port
		self.database = database
	#------------------------------------------
	def _get_port(self):
		return self.__port

	def _set_port(self, value):
		self.__port = int(value)

	port = property(_get_port, _set_port)
	#------------------------------------------
	def GetInfo(self):
		return (
			self.GetUser(),
			self.GetPassword(),
			self.GetHost(),
			self.GetPort(),
			self.GetDatabase(),
			self.GetProfile()
		)
	#------------------------------------------
	def GetInfoStr(self):
		# don't hand out passwords just like that
		info = "host:port=%s:%s, db=%s, user=%s, pw=??" % (
					self.GetHost(),
					str(self.GetPort()),
					self.GetDatabase(),
					self.GetUser()
				)
		return info
	#------------------------------------------
	def GetPGDB_DSN(self):
		host = self.GetHost()
		port = str(self.GetPort())
		# for local UNIX domain sockets connections: leave host/port empty
		# IH: *PLEASE* option of local TCP/IP connection must be available
#		if host in ['', 'localhost']:
#			host = ""
		if host == '':
			port = ''
		dsn = "%s:%s:%s:%s" % (
			host,
			self.GetDatabase(),
			self.GetUser(),
			self.GetPassword()
		)
		host_port = "%s:%s" % (host, port)
		return dsn, host_port
	#------------------------------------------
	def get_psycopg2_dsn(self):
		dsn_parts = []

		if self.database.strip() != '':
			dsn_parts.append('dbname=%s' % self.database)

		if self.host.strip() != '':
			dsn_parts.append('host=%s' % self.host)

		dsn_parts.append('port=%s' % self.port)

		if self.user.strip() != '':
			dsn_parts.append('user=%s' % self.user)

		if self.password.strip() != '':
			dsn_parts.append('password=%s' % self.password)

		return ' '.join(dsn_parts)
	#------------------------------------------
	def GetDBAPI_DSN(self):
		host = self.GetHost()
		port = str(self.GetPort())
		# for local UNIX domain sockets connections: leave host/port empty
#		if host in ['', 'localhost']:
#			host = ''
		if host == '':
			port = ''
		dsn = "%s:%s:%s:%s:%s" % (
			host,
			port,
			self.GetDatabase(),
			self.GetUser(),
			self.GetPassword()
		)
		return dsn
	#------------------------------------------
	def SetUser(self, user):
		self.user = user
	#------------------------------------------
	def GetUser(self):
		return self.user
	#------------------------------------------
	def SetDatabase(self, dbname):
		self.database = dbname
	#------------------------------------------
	def GetDatabase(self):
		return self.database
	#------------------------------------------
	def SetHost(self, host):
		self.host = host
	#------------------------------------------
	def GetHost(self):
		return self.host
	#------------------------------------------
	def SetPort(self, port):
		try:
			port = int (port)
		except ValueError:
			_log.warning("tried to set port to '%s', set to -1" % port)
			port = -1
		self.port = port
	#------------------------------------------
	def GetPort(self):
		return self.port
	#------------------------------------------
	def SetProfile(self, profile):
		self.__profile = profile
	#------------------------------------------
	def GetProfile(self):
		return self.__profile
	#------------------------------------------
	def Clear(self):
		"clears all connection information regarding user, password etc."

		self.user = "guest"
		self.password = ""
		self.host = ''
		self.port = 5432
		self.database = "gnumed_v9"
		self.__profile = 'default'

#====================================================================
if __name__ == "__main__" :

	import sys

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	print("Please somebody write a module test function here!")
