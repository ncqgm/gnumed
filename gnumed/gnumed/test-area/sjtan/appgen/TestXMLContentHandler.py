from xml.sax.handler import *
from xml.sax import *

class TestXMLContentHandler( ContentHandler):
	def __init__(self):
		ContentHandler.__init__(self)
		self.stack = []
		self.root = {}
		self.name = "root"
	def startDocument(self):
		print "found start"
		self.root = {}
		
	def endDocument(self):
		print "found end"
		print "root = ", self.root
	def startElement(self,name, attr):
		print "start element = " , name
		self.root[name] = {}
		if attr <> None:
			for a in attr.getNames():
				self.root[name][a] = attr.getValue(a)

		self.stack.append( self. root)
		self.root = self.root[name]
		
	def endElement(self, name):
		print "end element = " , name
		self.root = self.stack.pop()	
		
	

if __name__ == "__main__":
	f = file("appDefinition.xml")
	parse(f, TestXMLContentHandler())
	
