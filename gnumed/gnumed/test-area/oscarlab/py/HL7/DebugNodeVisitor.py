from AbstractNodeVisitor import AbstractNodeVisitor

class DebugNodeVisitor (AbstractNodeVisitor):

    def postVisitAction(self, node) :
    	print

    def nodeAction(self, node) :
	    print node

    def  propertyAction(self, s,  value) :
	    print s, ":", value
    
