#!/usr/bin/env python

# license GPL
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/tools/transferDBset.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Hilmar.Berger@gmx.de"
__license__ = "GPL"
#=====================================================
import sys,os
# location of our modules                                                       
sys.path.append(os.path.join('.', 'modules'))

import gmLog
gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)

import gmCfg
_cfg = gmCfg.gmDefCfgFile
import gmConfigCommon

import gmCLI
#=====================================================
def usage():
	print "Usage"
	print "-----"
	print """ 
	%s [-i|-e] [-user=<user>] [-machine=<machine>] filename
	  -i\timport from file
	  -e\texport to file
	  --user=<username> (Default: DEFAULT USER)
	  --machine=<machine> (Default: DEFAULT MACHINE)
	""" % sys.argv[0]
		  
	sys.exit(1)

if len(sys.argv)  <= 1:
	usage()

# search filename
filename = None
for opt in (sys.argv[1:]):
	if opt[0] == '-':
		continue
	else:
		filename = opt
		break
if filename is None:
	usage()

# get user
if gmCLI.has_arg('--user'):
	user = gmCLI.arg['--user']
	user2display = user
else:
	user = gmCfg.cfg_DEFAULT
	user2display = "DEFAULT USER"

# get machine
if gmCLI.has_arg('--machine'):
	machine = gmCLI.arg['--machine']
	machine2display = machine
else:
	machine = gmCfg.cfg_DEFAULT
	machine2display = "DEFAULT MACHINE"

print "User: %s\tMachine %s.\nConfig file: %s." % (user2display, machine2display, filename)

# import 
if gmCLI.has_arg('-i'):
	result = gmConfigCommon.importDBSet(filename, aMachine=machine, aUser = user)
	if result is not None:
		print "Import of file %s succeeded, %s parameters stored in DB." % (filename,result)
	else:
		print "Import of file %s failed" % filename
		
# export  
elif gmCLI.has_arg('-e'):
	result = gmConfigCommon.exportDBSet(filename, aMachine=machine, aUser = user)
	if result is not None:
		print "Export to file %s succeeded, %s parameters written to file." % (filename,result)
	else:
		print "Export to file %s failed" % filename
# wrong option
else: 
	usage()

sys.exit(0)
#=====================================================
# $Log: transferDBset.py,v $
# Revision 1.1  2004-02-25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.3  2003/10/26 21:34:45  hinnef
# - more clean up
#
# Revision 1.2  2003/10/26 21:17:39  hinnef
# - code clean up
#
# Revision 1.1  2003/10/02 20:03:16  hinnef
# initial revision
#
