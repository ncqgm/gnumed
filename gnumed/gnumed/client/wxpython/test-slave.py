"""Test driving an enslaved GnuMed client."""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/test-slave.py,v $
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
	print "ERROR: connection refused, have you started a slave GnuMed client ?"
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
detach = s.attach('slave-test')
print detach
time.sleep(3.000)

print "=> trying to raise GnuMed client to top of desktop"
print s.raise_gnumed()
time.sleep(3.000)

print "=> listing loaded plugins"
print s.get_loaded_plugins()
time.sleep(5.000)

print "=> raising a plugin that doesn't need an active patient"
print s.raise_plugin('gmManual')
print "=> trying to raise a plugin that needs an active patient"
print s.raise_plugin('gmClinicalWindowManager')
time.sleep(5.000)

print "=> knew it, need to lock into a patient first ..."
pat_lock = s.lock_into_patient('kirk, james')
print pat_lock

print "=> trying to raise plugin again"
print s.raise_plugin('gmClinicalWindowManager')
time.sleep(8.000)

print "=> switching to document display plugin"
print s.raise_plugin('gmShowMedDocs')
time.sleep(4.000)

print "=> cleaning up: unlocking patient"
print s.unlock_patient('wrong cookie')

print "=> unlocking again, correctly"
print s.unlock_patient(pat_lock[1])

print "=> detaching from macro processor (should fail)"
print s.detach('wrong cookie')

print "=> oh well, but now for real"
print s.detach(detach[1])
del s

#=====================================================================
# $Log: test-slave.py,v $
# Revision 1.1  2004-02-13 16:15:29  ncq
# - test drive GnuMed test slave
#
