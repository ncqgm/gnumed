
import weakref
import unittest 

class PropertyEvent:	
	def __init__(self,  source, name, oldValue,  newValue):
		self.source = source
		self.name = name
		self.oldValue = oldValue
		self.newValue = newValue
	
	def getSource(self):
		return self.source

	def getName(self):
		return self.name

	def getOldValue(self):
		return self.oldValue
	def getNewValue(self):
		return self.newValue



class PropertyListener:
	def propertyChanged(self, event):
		pass
	
class PropertySupport:
	def __init__(self, source):
		self.source = source
		self.weakMap = weakref.WeakKeyDictionary({})
		
	def addPropertyListener( self, l ):
		self.weakMap[l] = 1
	
	def firePropertyChanged(self,  name, oldValue , newValue ):
		self.firePropertyChanged2( self.source, name, oldValue, newValue )

	def firePropertyChanged2( self, source, name, oldValue, newValue):
		event = PropertyEvent( source, name, oldValue, newValue)
		self.firePropertyEvent(event)

	def firePropertyEvent(self, event):
		
		if event.getOldValue()  <> None and event.getOldValue() == event.getNewValue():
			return
		
		keys  = self.weakMap.keys()
		for listener in keys:
			listener.propertyChanged(event)
	

class PropertySupported:
	"""a base class for convenience property support firing to add to all attributes.
	   Example:
		   1. create a PropertyListener with the method propertyChanged(event)
		   2. create a class inheriting from PropertySupported 
		   3. create an instance o of (2)
		   4. o.addPropertyListener ( l )   where l is an instance of (1) 
		   
		   5.  o will fire a  
		   property change event and notifies the listener in (1)  for attribute "a" when 
		   	o.a = 1
				is executed.
 """
	def __init__(self):
		print "********** INITIALIZED PROPERTY SUPPORT "
		self.support = PropertySupport(self)
	
	def __setattr__(self, name, value):

		if name ==  "support":
			self.__dict__[name] = value
			return

		#print "name =", name, "value =", value, "name='support'?",name == "support"
		if self.__dict__.has_key(name):
			oldValue = self.__dict__[name]
		else:
			oldValue = None
		self.__dict__[name] = value


		self.support.firePropertyChanged(name,  oldValue, value)
	
	def addPropertyListener( self, listener):
		self.support.addPropertyListener( listener)
		

		
class TestPropertyListener:
	"""a test listener for the PropertySupport Test case"""
	def __init__( self, label):
		self.label = label
		self.map = {} 

	def hasProperty( self, name, value):
		if not self.map.has_key(name):
			return 0
		if self.map[name] == value:
			return 1
		return 0
		
	def propertyChanged(self, event):
		print self.label, "got event ", event.getSource(), event.getName(),"=", event.getNewValue(), " was = ", event.getOldValue()

		self.map[event.getName()] = event.getNewValue()

		
class PropSupportWeakRefTestCase(unittest.TestCase):
	"""test case to check the PropertySupport class works, and weakly references its listeners"""

	def setUp(self):
		self.propSupport = PropertySupport(self)
		a = TestPropertyListener('A')
		b = TestPropertyListener('B')
		c = TestPropertyListener('C')
		self.b = b
		self.listeners = [a, b, c]
		
		self.addPropertyListener(a)
		self.addPropertyListener(b)
		self.addPropertyListener(c)
		self.n = 3


	def addPropertyListener( self, listener):
		self.propSupport.addPropertyListener(listener)
	
	def allListenersHaveProperty(self , prop, value):
		yes = 1
		n = 0
		for x in self.listeners:
			if not x.hasProperty( prop, value):
				yes = 0
				continue
			n = n + 1
		self.n = n	
		return yes

	def getLastCountListeners(self):
		return self.n

	def firePropertyEvent(self, prop, oldValue, newValue):
		self.propSupport.firePropertyChanged(prop, oldValue, newValue)
	
	def runTest(self):
		self.firePropertyEvent( "apple", None, "ripe")
		
		self.failUnless( self.allListenersHaveProperty("apple", "ripe"), "failed all listener do not have apple ripe" )
		self.firePropertyEvent( "number", 0, 1)
		self.failUnless( self.allListenersHaveProperty("apple", "ripe") and self.allListenersHaveProperty("number", 1) , "failed all listener do not have apple-ripe and number-1" )
		list = ["a", "b", "c" ]
		self.firePropertyEvent( "list", [ "a", "b"], list )
		self.failUnless( self.allListenersHaveProperty("apple", "ripe")  and self.allListenersHaveProperty("number", 1) and self.allListenersHaveProperty( "list", list) , "failed all listener do not have apple-ripe and number-1 and list"  )


				
		self.failUnless( self.allListenersHaveProperty("apple", "ripe")  and self.allListenersHaveProperty("number", 1) and self.allListenersHaveProperty( "list", list) , "failed all listener do not have apple-ripe and number-1 and list"  )
		self.failUnless( self.getLastCountListeners() == 3)

		self.listeners.remove(self.b)
		self.firePropertyEvent( "alist", [ "a", "b"], list )
		self.failUnless( self.getLastCountListeners() == 3, "should be 3 listeners after removing one strong ref to self.b")
		self.b = None  # remove the last strong reference to listener b
		

		self.firePropertyEvent( "alist", [ "a", "b"], list )
	

		self.failUnless( self.allListenersHaveProperty("apple", "ripe")  \
		and self.allListenersHaveProperty("number", 1) \
		and self.allListenersHaveProperty( "alist", list)   , "failed all listener do not have apple-ripe and number-1 and list"  )

		self.failUnless( self.getLastCountListeners() == 2, "should be 2 listeners after removing all strong refs to self.b")
		#self.fail()	

		#self.failUnless( 1 == 2, "default fail" )

		print "tests have been run"


class TestPropSupported ( PropertySupported):

	def __init__(self):
		PropertySupported.__init__(self)
		self.a = 1
		self.b = "hello"
	

		
	
class PropSupportedTestCase(unittest.TestCase):
	"""this test case tests that listeners can listen in on attribute assignment of a 
	instance of any class inheriting from PropertySupported. """

	def setUp(self):
		self.test = TestPropSupported()
		self.l = TestPropertyListener("L")
		self.l2 = TestPropertyListener("M")
		self.test.addPropertyListener(self.l)
		
	def runTest(self):
		self.test.a = 2
		self.failUnless( self.l.hasProperty("a", 2) , "TestPropSupported.a should = 2")
		self.test.b = 3
		self.failUnless( self.l.hasProperty("b", 3) , "TestPropSupported.b should = 3")
		self.test.c = "apple"
		self.failUnless( self.l.hasProperty("c", "apple") , "TestPropSupported.c should = apple")
		self.test.addPropertyListener(self.l2)
		l = ["a list", "of things"]
		self.test.list = l
		self.failUnless( self.l.hasProperty("list", l) )
		self.failUnless( self.l2.hasProperty("list", l) )
		
		
		
if __name__ == "__main__":
	suite = unittest.TestSuite()
	
	testCase = PropSupportWeakRefTestCase()
	suite.addTest(testCase)
	
	testCaseSupported = PropSupportedTestCase()
	suite.addTest(testCaseSupported)

	result = unittest.TestResult()

	suite.run(result)
	print "ran ", result.testsRun
	print "result = ", result
	print 
	print "failures = ", result.failures
	print
	print "errors = ", result.errors
	print "ok"




	
	
	
	
