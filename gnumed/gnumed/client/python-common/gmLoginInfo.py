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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmLoginInfo.py,v $
# $Id: gmLoginInfo.py,v 1.10 2003-05-17 17:26:37 ncq Exp $
__version__ = "$Revision: 1.10 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

#====================================================================
class LoginInfo:
	"""a class to encapsulate Postgres login information to default database"""

	#private variables
	__user = 'guest'
	__ro_user = 'guest'
	__rw_user = ''
	__passwd = ''
	__host = 'localhost'
	__port = 5432
	__dbname = 'gnumed'
	__opt = ''
	__tty = ''
	__profile = 'default'
	#------------------------------------------
	def __init__(self, user, passwd, host='localhost', port=5432, database='gnumed', options='', tty='', profile='default'):
    		self.SetInfo(user, passwd, host, port, database, options, tty, profile)
	#------------------------------------------
	def SetInfo(self, user, passwd, host='localhost', port=5432, dbname='gnumed', opt='', tty='', profile='default'):
		self.SetUser(user)
		self.SetPassword(passwd)
		self.SetHost(host)
		self.SetPort(port)
		self.SetDatabase(dbname)
		#options are passed through unparsed to the backend
		self.SetOptions(opt)
		#debug terminal redirection, not used at present
		self.SetTTY(tty)
		#user profile toallow for different connection configurations
		self.SetProfile(profile)
	#------------------------------------------
	def GetInfo(self):
		return (
			self.GetUser(readonly=1),
			self.GetPassword(),
			self.GetHost(),
			self.GetPort(),
			self.GetDatabase(),
			self.GetOptions(),
			self.GetTTY(),
			self.GetProfile()
		)
	#------------------------------------------
	def GetInfoStr(self):
		# don't hand out passwords just like that
		info = "host:port=%s:%s, db=%s, user=%s, pw=??, opts=%s, tty=%s" % (
					self.GetHost(),
					str(self.GetPort()),
					self.GetDatabase(),
					self.GetUser(readonly=1),
					self.GetOptions(),
					self.GetTTY()
				)
		return info
	#------------------------------------------
	def GetPGDB_DSN(self, readonly=2):
		if readonly == 2:
			print "GetPGDB_DSN(): old style call, please convert"
			_log.Log(gmLog.lWarn, 'old style call, please convert')
		dsn = "%s:%s:%s:%s:%s:%s" % (
			self.GetHost(),
			self.GetDatabase(),
			self.GetUser(readonly),
			self.GetPassword(),
			self.GetOptions(),
			self.GetTTY()
		)
		host = "%s:%s" % (self.GetHost(), str(self.GetPort()))
		return dsn, host
	#------------------------------------------
	def GetDBAPI_DSN(self, readonly=2):
		if readonly == 2:
			print "GetDBAPI_DSN(): old style call, please convert"
			_log.Log(gmLog.lWarn, 'old style call, please convert')
		if self.GetHost () == "unix": # the virtual host "unix" is for UNIX socket connection
			host = ""
			port = "" # the port setting is ignored
		else:
			host = self.GetHost()
			port = str(self.GetPort())
		dsn = "%s:%s:%s:%s:%s:%s:%s" % (
			host,
			port,
			self.GetDatabase(),
			self.GetUser(readonly),
			self.GetPassword(),
			self.GetOptions(),
			self.GetTTY())
		return dsn
	#------------------------------------------
	def SetUser(self, user, readonly=2):
		# FIXME: once all callers are converted move this to readonly=1
		if readonly == 2:
			self.__user = user
			self.__ro_user = user
			self.__rw_user = '_%s' % user
			if len(user) > 0:
				if user[0] == '_':
					self.__ro_user = user[1:]
					self.__rw_user = user
		elif readonly == 1:
			self.__ro_user = user
		elif readonly == 0:
			self.__rw_user = user
			return self.__rw_user
		else:
			self.__ro_user = user
	#------------------------------------------
	def GetUser(self, readonly=2):
		# FIXME: once all callers are converted move this to readonly=1
		if readonly == 2:
			print "GetUser(): old style call, please convert"
			_log.Log(gmLog.lWarn, 'old style call, please convert')
			return self.__user
		elif readonly == 1:
			return self.__ro_user
		elif readonly == 0:
			return self.__rw_user
		else:
			return self.__ro_user
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
		self.__port = port
	#------------------------------------------
	def GetPort(self):
		return self.__port
	#------------------------------------------
	def SetOptions(self, opt):
		self.__opt = opt
	#------------------------------------------
	def GetOptions(self):
		return self.__opt
	#------------------------------------------
	def SetTTY(self, tty):
		self.__tty = tty
	#------------------------------------------
	def GetTTY(self):
		return self.__tty
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
		self.__ro_user = "guest"
		self.__rw_user = ""
		self.__passwd = ""
		self.__host = "localhost"
		self.__port = 5432
		self.__dbname = "gnumed"
		self.__opt= ""
		self.__tty = ""
		self.__profile = 'default'
		

#====================================================================
if __name__ == "__main__" :
	print "Please somebody write a module test function here!"

#====================================================================
# $Log: gmLoginInfo.py,v $
# Revision 1.10  2003-05-17 17:26:37  ncq
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
