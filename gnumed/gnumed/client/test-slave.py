"""Test driving an enslaved GnuMed client."""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/test-slave.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time
import xmlrpclib, socket

print "=> setting up connection to GnuMed client on localhost:9999"
s = xmlrpclib.ServerProxy('http://localhost:9999')

print "=> showing macro processor version"
try:
	print s.version()
except socket.error:
	print "ERROR: connection refused, have you started a slave GnuMed client on port 9999 ?"
	sys.exit(-1)

print "=> attaching to macro processor (should fail, missing cookie)"
detach = s.attach()
print detach

print "=> attaching to macro processor (should fail, wrong cookie)"
detach = s.attach('wrong cookie')
print detach

print "=> executing action in client (should fail since not attached)"
print s.raise_gnumed()

print "=> attaching to macro processor (should work)"
status, conn_auth = s.attach('slave-test')
print status, conn_auth
time.sleep(3)

print "=> trying to raise GnuMed client to top of desktop"
print s.raise_gnumed(conn_auth)
time.sleep(3)

print "=> listing loaded plugins (should fail)"
print s.get_loaded_plugins('wrong auth')
time.sleep(5)

print "=> listing loaded plugins"
print s.get_loaded_plugins(conn_auth)
time.sleep(5)

print "=> raising a plugin that doesn't need an active patient"
print s.raise_plugin(conn_auth, 'gmManual')
print "=> trying to raise a plugin that needs an active patient"
print s.raise_plugin(conn_auth, 'gmClinicalWindowManager')
time.sleep(5)

print "=> knew it, need to lock into a patient first ..."
status, unlock_auth = s.lock_into_patient(conn_auth, 'kirk, james')
print status, unlock_auth

print "=> trying to raise plugin again"
print s.raise_plugin(conn_auth, 'gmClinicalWindowManager')
time.sleep(8)

print "=> switching to document display plugin"
print s.raise_plugin(conn_auth, 'gmShowMedDocs')
time.sleep(4)

print "=> cleaning up: unlocking patient"
print s.unlock_patient(conn_auth, 'wrong cookie')

print "=> unlocking again, correctly"
print s.unlock_patient(conn_auth, unlock_auth)

print "=> detaching from macro processor (should fail)"
print s.detach('wrong cookie')

print "=> oh well, but now for real"
print s.detach(conn_auth)
del s

#=====================================================================
# $Log: test-slave.py,v $
# Revision 1.1  2004-03-15 15:29:30  ncq
# - moved here from wxpython/
#
# Revision 1.2  2004/02/17 10:47:22  ncq
# - adapt to creds passing on every RPC
#
# Revision 1.1  2004/02/13 16:15:29  ncq
# - test drive GnuMed test slave
#
