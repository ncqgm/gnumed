#!/usr/bin/env python
###############################################################
# This is a tool to find places marked with FIXME that need work.
#
# example:
# --------
# FIXME: plugin loading should be optional
#--------------------------------------------------------------
# @author: Karsten Hilbert
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @Date: $Date: 2004-02-25 09:30:13 $
# @version $Revision: 1.1 $ $Date: 2004-02-25 09:30:13 $ $Author: ncq $
###############################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/tools/Attic/find_todo.py,v $
__version__ = "$Revision"

import string, sys, fileinput

if len(sys.argv) < 2:
	print "Usage: find_todo.py <a_python_script> <a_python_script> ..."
	sys.exit(1)

print "Searching for places to fix in", sys.argv[1:]

prev_file = ""

for line in fileinput.input():
	curr_file = fileinput.filename()

	if prev_file != curr_file:
		print "%s:" % curr_file
		prev_file = curr_file

	if string.find(line, "FIXME") != -1:
		line_no = fileinput.filelineno()
		line = string.replace(line, '\015','')
		line = string.replace(line, '\012','')
		print line_no, ":", line

#=====================================================================
# $Log: find_todo.py,v $
# Revision 1.1  2004-02-25 09:30:13  ncq
# - moved here from python-common
#
