#this module demostrates the simplest case of event sending and handling
#via the gmDispatcher module. Read the gmDispatcher inline documentation
#for the more powerful features

import gmDispatcher


#this module could be a real module in a separate file
class module1:
	def __init__(self):
		print "instance of class test is initialized\n"

	#example callback function
	def callback(self, param):
		#no default parameter; if 'param' is not passed, an exception will be raised
		print "-> callback of module1 called with parameter %s\n" % param

	#a little bit more meaningful callback function
	def OnAllergy(self, allergy_id):
		#no default parameter; if 'allergy_id' is not passed, an exception will be raised
		print "-> Requerying allergy database for id = %d" % allergy_id


#this module could be a real module in a separate file
class module2:
	def __init__(self):
		print "instance of class test2 is initialized\n"
		#look at how we pass the method __call__ as 'self':
		gmDispatcher.connect(self, 'weird')
	#define a callback function that does something, and the
	#posts an event that may cause other modules to do something else
	def callback(self, otherparam='default'):
		#if 'otherparam' is not passe as parameter, there is a default
		print "-> callback of test2 called with parameter %s\n" % otherparam
		gmDispatcher.send('allergy_changed', sender=None, allergy_id=1)
		
	def __call__(self, param):
		print "\nThis one shows how to use the dispatcher within a class definition"
		print "it works:", param


#create an instance of each of the two classes / modules
dummy = module1()
dummy2=module2()

#register the callback functions
gmDispatcher.connect(dummy.callback, 'some signal')
gmDispatcher.connect(dummy.OnAllergy, 'allergy_changed')
gmDispatcher.connect(dummy2.callback, 'some signal')

#now post a message (event) to all receivers
#who have registered an interest in the event "some signal"
#In the case of module2, the callback function catching the event will
#post another message which should be handled by module1's
#'OnAllergy" callback function
print "\n# Posting the event 'some signal' with the parameters 'abc' and 'def'"
print "# Read the code and learn why only parameter 'abc' has been handled\n"

gmDispatcher.send('some signal', param='abc', ignoredparam="def")
gmDispatcher.send('weird', param='abc', ignoredparam="def")

print "\n# Now we send a message without a required parameter. See what happens:\n"
gmDispatcher.send('allergy_changed', sender=None, param='abc')
