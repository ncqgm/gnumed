"""Test driving an enslaved GnuMed client.

This script demonstrates how to script a GNUmed client.

To run the test you must have a GNUmed client running
with --slave and

 [workplace]
  slave personality = slave-test
  xml-rpc port = 9999 (the default)

in the config file.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/test-slave.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time
import xmlrpclib, socket

print "=> setting up connection to GNUmed client on localhost:9999"
srv = xmlrpclib.ServerProxy('http://localhost:9999')

print "=> showing macro processor version"
try:
	print srv.version()
except socket.error:
	print "ERROR: connection refused, have you started a slave GNUmed client on port 9999 ?"
	sys.exit(-1)

print "=> attaching to macro processor (should fail, missing cookie)"
detach = srv.attach()
print detach

print "=> attaching to macro processor (should fail, wrong cookie)"
detach = srv.attach('wrong cookie')
print detach

print "=> executing action in client (should fail, not attached)"
print srv.raise_gnumed()

print "=> attaching to macro processor (should work, returns (status, auth cookie))"
status, conn_auth = srv.attach('slave-test')
print status, conn_auth
time.sleep(3)

print "=> trying to raise GNUmed client to top of desktop"
print srv.raise_gnumed(conn_auth)
time.sleep(3)

print "=> listing loaded plugins (should fail, wrong auth cookie)"
print srv.get_loaded_plugins('wrong auth')
time.sleep(5)

print "=> listing loaded plugins"
print srv.get_loaded_plugins(conn_auth)
time.sleep(5)

plugin = 'gmManual'
print "=> raising a plugin that doesn't need an active patient (%s)" % plugin
print srv.raise_notebook_plugin(conn_auth, plugin)
time.sleep(3)

plugin = 'XXX-no-such-plugin-XXX'
print "=> raising a plugin that is not loaded (%s)" % plugin
print srv.raise_notebook_plugin(conn_auth, plugin)
time.sleep(3)

plugin = 'gmEMRJournalPlugin'
print "=> trying to raise a plugin that needs an active patient (%s)" % plugin
print srv.raise_notebook_plugin(conn_auth, plugin)
time.sleep(5)

print "=> knew it, need to lock into a patient first (returns (status, unlock cookie))"
status, unlock_auth = srv.lock_into_patient(conn_auth, 'kirk, james')
print status, unlock_auth

print "=> trying to raise plugin again"
print srv.raise_notebook_plugin(conn_auth, plugin)
time.sleep(8)

plugin = 'gmShowMedDocs'
print "=> switching to document display plugin (%s)" % plugin
print srv.raise_notebook_plugin(conn_auth, plugin)
time.sleep(4)

print "=> cleaning up: unlocking patient (should fail, wrong cookie)"
print srv.unlock_patient(conn_auth, 'wrong cookie')

print "=> unlocking again (should work)"
print srv.unlock_patient(conn_auth, unlock_auth)

print "=> detaching from macro processor (should fail, wrong cookie)"
print srv.detach('wrong cookie')

print "=> oh well, but now for real"
print srv.detach(conn_auth)
del srv

#=====================================================================
# $Log: test-slave.py,v $
# Revision 1.5  2007-09-04 23:27:12  ncq
# - improve docs
#
# Revision 1.4  2005/11/29 18:56:05  ncq
# - general polishing
#
# Revision 1.3  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.2  2004/03/15 22:40:17  ncq
# - added docs on how to use this
#
# Revision 1.1  2004/03/15 15:29:30  ncq
# - moved here from wxpython/
#
# Revision 1.2  2004/02/17 10:47:22  ncq
# - adapt to creds passing on every RPC
#
# Revision 1.1  2004/02/13 16:15:29  ncq
# - test drive GNUmed test slave
#
