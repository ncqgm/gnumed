
from wxPython.wx import *
#from PropertySupport import *
if not "../business" in sys.path:
	sys.path.append("../python-common")
	sys.path.append("../business")

sys.path.append("../python-common")
import gmLog 
import sys, traceback
import gmTmpPatient

# why do we need a special logger here ?
logger = gmLog.cLogger( gmLog.cLogTargetConsole())
#logger = gmLog.gmDefLog

logger.SetInfoLevel()

class TestEvents:

	def __init__(self):
		pass
		

	def  test_checkbox(self,  editarea):
		# wouldn't it make sense to look in
		# editarea.__dict__['edit_fields'] ?
		map = editarea.__dict__
		for k,v  in map.items():
			# and then check k.__class__.__name__ or so ?
			# as long as no subtypes. is there a isAssignableFrom(parent_class) function like java?
			# test code: sort out later.
			if k[0:2] == "cb":
				EVT_CHECKBOX(v, v.GetId(),self.checkClicked)
			
			if k[0:3] == "btn":
				EVT_BUTTON( v, v.GetId(), self.buttonPressed)

	def checkClicked(self, evt):
		try:
			logger.Data( "Got check box " +  str(evt) +  "from object with id" + str(evt.GetId()) +  "obj=" + str(evt.GetEventObject()), 4 )
		except:
			logger.LogException("unable to get event", sys.exc_info())

			

	def buttonPressed(self, evt):
		try:

			section= evt.GetEventObject().owner.GetName()

			logger.Data("Button with label " +  evt.GetEventObject().GetLabel() + " pressed : owner of buttons = " + evt.GetEventObject().owner.GetName() , 4)
			
			list = evt.GetEventObject().owner.input_fields
			values = {} 
			for n,f in list.items():
				values[n] = str(f.GetValue())
				
			
			logger.Data("Values of " + section + " are " + str(values), 4 )
			

			if section == "allergy":
				# Test Code: change ASAP.	
				
		                try:
			        	myPatient = gmTmpPatient.gmCurrentPatient()
					clinicalRecord = myPatient['clinical record']
					clinicalRecord.create_allergy(values)
				except:
					logger.LogException("unable to setup allergy", sys.exc_info())
		except:
			logger.LogException("unable to get event", sys.exc_info())

			
					


if __name__=="__main__":
	logger.Data("Information")
	try:
		a
	except:	
		logger.LogException("TestException", sys.exc_info())
	
