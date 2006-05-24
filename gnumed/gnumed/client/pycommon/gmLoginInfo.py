#############################################################################
#
# gmLoginInfo - a class to encapsulate Postgres login information
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: none
# @change log:
#	01.06.2001 hherb initial implementation
#	26.10.2001 hherb comments added
#	08.02.2001 hherb made DB API 2.0 compatible
#
# @TODO:
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmLoginInfo.py,v $
# $Id: gmLoginInfo.py,v 1.6 2006-05-24 12:50:21 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

import gmLog

#====================================================================
class LoginInfo:
	"""a class to encapsulate Postgres login information to default database"""

	# private variables
	__user = 'guest'
	__passwd = ''
	__host = ''
	__port = 5432
	__dbname = 'gnumed_v2'
	__profile = 'default'
	#------------------------------------------
	def __init__(self, user, passwd, host, port=5432, database='gnumed_v2', profile='default'):
		self.SetInfo(user, passwd, host, port, database, profile)
	#------------------------------------------
	def SetInfo(self, user, passwd, host='', port=5432, dbname='gnumed_v2', profile='default'):
		self.SetUser(user)
		self.SetPassword(passwd)
		self.SetHost(host)
		self.SetPort(port)
		self.SetDatabase(dbname)
		# user profile to allow for different connection configurations
		self.SetProfile(profile)
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
		self.__user = user
	#------------------------------------------
	def GetUser(self):
		return self.__user
	#------------------------------------------
	def SetPassword(self, passwd):
		self.__passwd = passwd
	#------------------------------------------
	def GetPassword(self):
		return self.__passwd
	#------------------------------------------
	def GetPasswordHash(self):
		return sha.new(self.__passwd).digest()
	#------------------------------------------
	def SetDatabase(self, dbname):
		self.__dbname = dbname
	#------------------------------------------
	def GetDatabase(self):
		return self.__dbname
	#------------------------------------------
	def SetHost(self, host):
		self.__host = host
	#------------------------------------------
	def GetHost(self):
		return self.__host
	#------------------------------------------
	def SetPort(self, port):
		try:
			port = int (port)
		except ValueError:
			gmLog.gmDefLog.Log (gmLog.lWarn, "tried to set port to '%s', set to -1" % port)
			port = -1
		self.__port = port
	#------------------------------------------
	def GetPort(self):
		return self.__port
	#------------------------------------------
	def SetProfile(self, profile):
		self.__profile = profile
	#------------------------------------------
	def GetProfile(self):
		return self.__profile
	#------------------------------------------
	def Clear(self):
		"clears all connection information regarding user, password etc."

		self.__user = "guest"
		self.__passwd = ""
		self.__host = ''
		self.__port = 5432
		self.__dbname = "gnumed_v2"
		self.__profile = 'default'

#====================================================================
if __name__ == "__main__" :
	print "Please somebody write a module test function here!"

#====================================================================
# $Log: gmLoginInfo.py,v $
# Revision 1.6  2006-05-24 12:50:21  ncq
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
