
from wxPython.wx import *
from PropertySupport import *

sys.path.append("../python-common")
from gmLog import *
import sys, traceback


logger = cLogger( cLogTargetConsole())
logger.SetInfoLevel()

class TestEvents:

	def  test_checkbox(self,  editarea):
		map = editarea.__dict__
		for k,v  in map.items():
			if k[0:2] == "cb":
				EVT_CHECKBOX(v, v.GetId(),self.checkClicked)
			
			if k[0:3] == "btn":
				EVT_BUTTON( v, v.GetId(), self.buttonPressed)

	def checkClicked(self, evt):
		try:
			logger.Info( "Got check box " +  str(evt) +  "from object with id" + str(evt.GetId()) +  "obj=" + str(evt.GetEventObject()), 4 )
		except:
			logger.LogException("unable to get event", sys.exc_info())

	def buttonPressed(self, evt):
		try:
			logger.Info("Button with label " +  evt.GetEventObject().GetLabel() + " pressed : owner of buttons = " + evt.GetEventObject().owner.GetName() , 4)
			
			list = evt.GetEventObject().owner.input_fields
			values = {} 
			for n,f in list.items():
				values[n] = str(f.GetValue())
				
			
			logger.Info("Values of " + evt.GetEventObject().owner.GetName() + " are " + str(values), 4 )


			
			
		except:
			logger.LogException("unable to get event", sys.exc_info())

			
					


if __name__=="__main__":
	logger.Info("Information")
	try:
		a
	except:	
		logger.LogException("TestException", sys.exc_info())
	
