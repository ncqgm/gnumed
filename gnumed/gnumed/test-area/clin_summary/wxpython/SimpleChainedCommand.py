from SimpleCommand import * 

class SimpleChainedCommand(Command):

	def setNextCommand(self, command):
		self.next = command

	def execute( self, source, args):
		self.next.execute( source, args)
		return None
			
