



import sys
import time

from HL7.DebugNodeVisitor import DebugNodeVisitor
debugVisitor = DebugNodeVisitor()

from HL7.Message import Message

	
	
def getMessagesFromLines(lines):
	m = None
	msgs = []
	for l in lines:
		#print l
		if l[0:3] == "MSH":
			if m :
				msgs.append(m)
		
			m = Message(time.strftime("%c"))
			print "created ", m

		if m:
			m.Parse(l)
	
	if m:
		msgs.append(m)

	return msgs

def getMessages(raw_messages):
	msgs = []
	for data in raw_messages:
		lines = data.split("\n")
		msgs.extend(getMessagesFromLines(lines))
	return msgs

def printMessage(m):
	global debugVisitor
	m.accept(debugVisitor)

def printMessages(msgs):
	for m in msgs:
		printMessage(m)
	
if __name__=="__main__":

	filename = sys.argv[1]

	if filename[-3:] == 'xml':
		from HL7.DocumentUtil import parseXML
		l = parseXML(filename)
	else:
		data = []
		for x in file(filename, "r"):
			data.append(x)
		if len(data) == 1:
			data = data[0].split("\r")
		l =  [ "\n".join(data) ]
		#print l

	messages = getMessages(l)
	printMessages(messages)

		
	

