#!/usr/bin/env python

# license GPL
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/tools/Attic/set-conf_opt.py,v $
__version__ = "$Revision: 1.2 $"
#=====================================================
import sys
sys.path.append('modules')

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmCLI
#=====================================================
def usage():
	print "Usage"
	print "-----"
	print " set-conf_opt --conf-file=<file> --section=<section> --option=<option> --value=<value>"
	sys.exit(1)

if _cfg is None:
	usage()

if not gmCLI.has_arg('--section'):
	usage()
if not gmCLI.has_arg('--option'):
	usage()
if not gmCLI.has_arg('--value'):
	usage()

_cfg.set(gmCLI.arg['--section'], gmCLI.arg['--option'], gmCLI.arg['--value'])
_cfg.store()

sys.exit(0)
#=====================================================
# $Log: set-conf_opt.py,v $
# Revision 1.2  2007-12-11 15:39:34  ncq
# - logging
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.1  2003/01/30 09:43:56  ncq
# - try to make Debian a little more happy
#
