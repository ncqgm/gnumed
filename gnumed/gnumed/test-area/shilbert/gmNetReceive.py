#!/usr/bin/python
import sys, xmpp, os, signal, time

jid="ncq@jabber.gnumed.de"
pwd="yourpasswordhere"

jid=xmpp.protocol.JID(jid)

cl = xmpp.Client(jid.getDomain(), debug=[])

def messageCB(conn,msg):
    print "Sender: " + str(msg.getFrom())
    print "Content: " + str(msg.getBody())
    print msg

def StepOn(conn):
    print "hello"
    try:
	conn.Process(1)
    except KeyboardInterrupt:
	return 0
    return 1

def GoOn(conn):
    while StepOn(conn):
	pass

def Main():
    if cl.connect(server=('jabber.gnumed.de',5223)) == "":
        print "not connected"
        sys.exit(0)
    else:
	print "connected"
	
    if cl.auth(jid.getNode(),pwd) == None:
	print "authentication failed"
	sys.exit(0)
    else:
	print "doing fine"

    cl.RegisterHandler(unicode('message'), messageCB)    
    cl.sendInitPresence()
    
    GoOn(cl)
    
Main()
