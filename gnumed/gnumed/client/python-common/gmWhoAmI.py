#===================================================
__version__ = "$Revision: 1.2 $"
__author__ = "Hilmar.Berger@gmx.de"
__license__ = "GPL"

import gmGuiBroker

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

#===================================================
class cWhoAmI:
	"""
	This class holds information on who and on which machine we are.
	Right now we can only determine these information if
	a) guiBroker is running and has 'workplace' and 'user' set or
	b) we have set this manually via setUser() or setMachine() before
	"""
#	_GuiBroker = None
	_user = None
	_machine = None

	def __init__(self):
		self.mGuiBroker = gmGuiBroker.GuiBroker()
		cWhoAmI._User = None
		cWhoAmI._mMachine = None

	def getUser(self):
		"""
		Returns: user name if set via GuiBroker or manually via SetUser()
			 None otherwise
		"""
		if self.mGuiBroker.has_key('currentUser'):
			return self.mGuiBroker['currentUser']
		else:
			return cWhoAmI._user
	
	
	def getMachine(self):
		"""
		Returns: machine name if set via GuiBroker or manually via SetMachine()
			 None otherwise
		"""
		if self.mGuiBroker.has_key('workplace_name'):
			return self.mGuiBroker['workplace_name']
		else:
			return cWhoAmI._machine
	
	def setUser(self,aUser):
		""" Set user name for this session."""
		cWhoAmI._user = aUser
	
	def setMachine(self,aMachine):
		""" Set machine name for this session."""
		cWhoAmI._machine = aMachine 

#===================================================
# $Log: gmWhoAmI.py,v $
# Revision 1.2  2003-11-17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/09/03 17:29:41  hinnef
# added gmWhoAmI to facilitate user/machine determination
#
