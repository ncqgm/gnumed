from SimpleRecordPanel import *
from SimpleUIFactory import *

class SimpleHorizontalDialogFactory ( SimpleUIFactory):

	def getUI( self, parent, id, data) :
		frame = data[0]
		list = data[1]
		return SimpleRecordPanel(  parent, frame, list,  1)

