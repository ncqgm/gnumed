
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

	def checkClicked(self, evt):
		try:
			logger.Info( "Got check box " +  str(evt) +  "from object with id" + str(evt.GetId()) +  "obj=" + str(evt.GetEventObject()), 4 )
		except:
			logger.LogException("unable to get event", sys.exc_info())
					


if __name__=="__main__":
	logger.Info("Information")
	try:
		a
	except:	
		logger.LogException("TestException", sys.exc_info())
	
