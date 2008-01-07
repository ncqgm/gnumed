############################################################################
# gmLoginInfo - a class to encapsulate Postgres login information
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmLoginInfo.py,v $
# $Id: gmLoginInfo.py,v 1.16 2008-01-07 19:49:12 ncq Exp $
__version__ = "$Revision: 1.16 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging

_log = logging.getLogger('gm.database')
_log.info(__version__)
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
	print "Please somebody write a module test function here!"

#====================================================================
# $Log: gmLoginInfo.py,v $
# Revision 1.16  2008-01-07 19:49:12  ncq
# - bump db version
#
# Revision 1.15  2007/12/12 16:17:15  ncq
# - better logger names
#
# Revision 1.14  2007/12/11 14:30:44  ncq
# - std logging
#
# Revision 1.13  2007/10/22 12:37:59  ncq
# - default db change
#
# Revision 1.12  2007/06/11 20:23:45  ncq
# - bump database version
#
# Revision 1.11  2007/04/02 14:31:17  ncq
# - v5 -> v6
#
# Revision 1.10  2007/03/08 11:36:45  ncq
# - starting to simplify
#
# Revision 1.9  2007/02/06 12:08:39  ncq
# - upgrade to gnumed_v5
#
# Revision 1.8  2006/10/08 15:10:51  ncq
# - add comment on cBorg
#
# Revision 1.7  2006/09/21 19:46:38  ncq
# - attributes should really be .something, not .__something
# - change default to "gnumed_v3"
# - add get_psycopg2_dsn() but will go again
#
# Revision 1.6  2006/05/24 12:50:21  ncq
# - now only empty string '' means use local UNIX domain socket connections
#
# Revision 1.5  2006/02/26 18:33:00  ncq
# - change default to gnumed_v2
#
# Revision 1.4  2004/09/13 09:32:21  ncq
# - remove support for tty/backend opts, we never used them, they
#   are only documented for old PostgreSQL versions, so axe them
#
# Revision 1.3  2004/07/17 20:54:50  ncq
# - remove user/_user workaround
#
# Revision 1.2  2004/04/21 14:27:15  ihaywood
# bug preventing backendlistener working on local socket connections
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.17  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.16  2003/09/17 11:15:39  ncq
# - make local TCP/IP available for all DBA types
#
# Revision 1.15  2003/09/17 03:00:59  ihaywood
# support for local inet connections
#
# Revision 1.14  2003/08/17 17:58:09  ncq
# - whitespace fix
#
# Revision 1.13  2003/06/26 02:31:23  ihaywood
# Fix for non-integer port values
#
# Revision 1.12  2003/06/16 09:52:04  ncq
# - really make local connections go via sockets
#
# Revision 1.11  2003/06/14 22:41:30  ncq
# - leave host/port blank for UNIX domain socket authentication data
#
# Revision 1.10  2003/05/17 17:26:37  ncq
# - start clean up of _user/user mess:
#   - introduce __ro/rw_user
#   - add "readonly" parameter to GetUser(), Get*_DSN() and SetUser()
#   - make SetUser()/Get* smart about old style use, log warning
#
# Revision 1.9  2003/01/16 14:45:03  ncq
# - debianized
#
# Revision 1.8  2003/01/04 09:34:16  ncq
# - missing self. in GetDBAPI_DSN
#
# Revision 1.7  2003/01/04 09:05:17  ncq
# - added CVS tracking keywords
#


# old change log:
#	01.06.2001 hherb initial implementation
#	26.10.2001 hherb comments added
#	08.02.2001 hherb made DB API 2.0 compatible
