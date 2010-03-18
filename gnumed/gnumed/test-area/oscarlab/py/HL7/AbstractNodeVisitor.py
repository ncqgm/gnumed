
class AbstractNodeVisitor:
	
	def visit(self,node):
		self.nodeAction(node)
		for prop in node.getProperties():
			self.propertyAction(prop, node.get(prop, None))
	
		self.postVisitAction(node)

	def postVisitAction(self, node):
		pass

    	def nodeAction(self, node):
	    	pass

	def propertyAction(self, name, value):
		pass

	def visitPID(self, pid): 
		self.visit(pid)

		for container in pid.getContainers():
			container.accept(self)
			
		for note in pid.getNotes():
			note.accept(self)

	def visitPIDContainer(self, container) :
		self.nodeAction(container)

		if (container.getOBR() <> None) :
		    container.getOBR().accept(self)

		if ( container.getORC() <> None ) :
		    container.getORC().accept(self)

    	def visitOBR(self, obr) :
		self.visit(obr);
		for obx in obr.getOBXS():
			obx.accept(self)

		for note in obr.getNotes():
			note.accept(self)

	def  visitOBX(self, obx) :
		self. visit(obx)
