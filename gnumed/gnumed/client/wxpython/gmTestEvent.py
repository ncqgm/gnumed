from wxPython.wx import *
from PropertySupport import *
import sys, traceback


class TestEventListener(PropertyListener):
        def propertyChanged(self, event):
		
                if event.getName()[0:2] == "cb":
                        print "*  TestEvent got ", event.getNewValue()
                        chbox = event.getNewValue()
			try:
				EVT_CHECKBOX(chbox, chbox.GetId(),self.checkClicked)
			except:
				traceback.print_exc()
		else:
			print "**** ", event.getName() , " does not begin with cb" 

	def checkClicked(self, evt):
		try:
			print "Got check box ", evt, "from object with id", evt.GetId(), "obj=", evt.GetEventObject()
		except:
			traceback.print_exc()
		


if __name__=="__main__":
	validator = TestEventListener()
	
