import PersonIdService__POA
import omniORB
import CosNaming
import sys

from SqlTraits import * 
from PlainConnectionProvider import *

from  StartIdentificationComponent import StartIdentificationComponent

class IDComponentResolver :
	def __init__( self, initContextName="NameService",
		contextCorbaloc = 'corbaloc:iiop:localhost:5002/NameService'):

		self.initContextName = initContextName
		self.contextCorbaloc = contextCorbaloc
		self.__init_orb()
		self.local = '-local' in sys.argv

	def __init_orb(self):
		self.orb = omniORB.CORBA.ORB_init(['-','-ORBInitRef', '%s=%s' %(self.initContextName, self.contextCorbaloc) ])


	def getORB(self) :
		return self.orb

	def getInitialContext(self):
		orb = self.getORB()
		o = orb.resolve_initial_references(self.initContextName)
		return  o._narrow(CosNaming.NamingContextExt)


	def getIdentificationComponent(self, path = None):
		if self.local:
			print "USING LOCAL startIdentificationComponent"
			return getStartIdentificationComponent()

		if path == None:
			path = "us/nm/state/doh/Pilot"

		context = self.getInitialContext()
		list = self.changePathToNameComponentList(path)
		if debug:
			for x in list:
				print x.__dict__
		o2 = context.resolve(list)
		ids = o2._narrow(PersonIdService.IdentificationComponent)
		return ids

	def changePathToNameComponentList(self, path):
		return [ CosNaming.NameComponent(n, "") for n in path.split('/')]

def testAttributes():
	resolver = IDComponentResolver()
	if '-gnumed' in sys.argv:
		path = 'gnumed'
	else:
		path = None
	ids = resolver.getIdentificationComponent(path)
	traits =  ids._get_supported_traits()
	for x in traits:
		print x.__dict__
	#this will fail with open-emed pids.
	#print ids._get_supported_properties()


def testSequentialAccess():
	"""Test the methods of the sequential_access identification component"""
	import TestSequentialAccess
	global debug
	TestSequentialAccess.debug = debug
	TestSequentialAccess.test()

def testIdMgr():
	import TestIdMgr
	global debug
	TestIdMgr.debug = debug
	TestIdMgr.test()

def testIdentifyPerson():
	import TestIdentifyPerson
	global debug
	TestIdentifyPerson.debug = debug
	TestIdentifyPerson.test()

def testProfileAccess():
	import TestProfileAccess
	global debug
	TestProfileAccess.debug = debug
	TestProfileAccess.test()

def testIdentifyPerson():
	import TestIdentifyPerson
	global debug
	TestIdentifyPerson.test()

def getStartIdentificationComponent():
	from IdentifyPerson_i import IdentifyPerson_i
	from  ProfileAccess_i import ProfileAccess_i
	from SequentialAccess_i import SequentialAccess_i
	from IdMgr_i import IdMgr_i
	return StartIdentificationComponent( ProfileAccess_i(), SequentialAccess_i(), IdentifyPerson_i(), IdMgr_i() )


def doTest( m):
	print
	for i in xrange(0,2):
		print "*" * 60

	print "RUNNING ", m
	for i in xrange(0,2):
		print "*" * 60
	m()

if __name__== "__main__":
	global debug
	debug = ( "-debug" in sys.argv)
	resolver = IDComponentResolver()
	ids = resolver.getIdentificationComponent()
	if '-profile' in sys.argv:
		import profile
		profile.run('testAttributes()')
		profile.run('testSequentialAccess()')
		profile.run('testIdMgr()')
		profile.run('testIdentifyPerson()')
		profile.run('testProfileAccess()')
		sys.exit(0)

	doTest(testAttributes)
	doTest(testSequentialAccess)
	doTest(testIdMgr)
	doTest(testIdentifyPerson)
	doTest(testProfileAccess)
	doTest(testIdentifyPerson)
