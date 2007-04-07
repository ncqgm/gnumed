#!/usr/bin/python
import sys,os,xmpp

msg="Hello World!"
jid="ncq@jabber.gnumed.de"
pwd="yourpasswordhere"

recipient="mkbigcash@jabber.gnumed.de"

jid=xmpp.protocol.JID(jid)

cl=xmpp.Client(jid.getDomain(),debug=['always'])

if cl.connect(server=('jabber.gnumed.de',5223)) == "":
    print "not connected"
    sys.exit(0)


if cl.auth(jid.getNode(),pwd) == None:
    print "authentication failed"
    sys.exit(0)
    
cl.send(xmpp.protocol.Message(recipient,msg))

cl.disconnect()

