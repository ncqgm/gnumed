#!/usr/bin/python
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
#
# @TODO:
############################################################################

class LoginInfo:
	"a class to encapsulate Postgres login information"

	#private variables
	__user = 'guest'
	__passwd = ''
	__host = 'localhost'
	__port = 5432
	__dbname = 'gnumed'
	__opt = ''
	__tty = ''
	__profile = 'default'


	def __init__(self, user, passwd, host='localhost', port=5432, database='gnumed', options='', tty='', profile='default'):
    		self.SetInfo(user, passwd, host, port, database, options, tty, profile)


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

	def GetInfo(self):
        	return self.GetUser(), self.GetPassword(), self.GetHost(), self.GetPort(), \
		self.GetDatabase(), self.GetOptions(), self.GetTTY(), self.GetProfile()


    	def SetUser(self, user):
		self.__user = user

	def GetUser(self):
		return self.__user

	def SetPassword(self, passwd):
		self.__passwd = passwd

	def GetPassword(self):
		return self.__passwd

	def GetPasswordHash(self):
		return sha.new(self.__passwd).digest()

	def SetDatabase(self, dbname):
		self.__dbname = dbname

	def GetDatabase(self):
		return self.__dbname

	def SetHost(self, host):
		self.__host = host

	def GetHost(self):
		return self.__host

	def SetPort(self, port):
		self.__port = port

	def GetPort(self):
		return self.__port

	def SetOptions(self, opt):
		self.__opt = opt

	def GetOptions(self):
		return self.__opt

	def SetTTY(self, tty):
		self.__tty = tty

	def GetTTY(self):
		return self.__tty

	def SetProfile(self, profile):
		self.__profile = profile

	def GetProfile(self):
		return self.__profile

	def Clear(self):
		"clears all connection information regarding user, password etc."

		self.__user = ""
		self.__passwd = ""
		self.__host = "localhost"
		self.__port = 5432
		self.__dbname = "gnumed"
		self.__opt= ""
		self.__tty = ""
		self.__profile = default


if __name__ == "__main__" :
	print "Please somebody write a module test function here!"
